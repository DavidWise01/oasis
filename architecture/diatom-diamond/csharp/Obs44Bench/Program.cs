// OBS44 C# Release benchmark: exact dual recovery and bounded-channel mode.
// No neural model is run. Rates count OBS44 symbolic glyphs/s.
using System.Diagnostics;
using System.Text.Json;
using Oasis.Obs;

static void Require(bool condition,string note){if(!condition)throw new Exception("OBS44 failed: "+note);}
static void Reject(Action action,string note)
{
    bool threw=false;
    try{action();}catch(ArgumentException){threw=true;}catch(FormatException){threw=true;}
    Require(threw,"Expected rejection: "+note);
}
static int SelfTest()
{
    int checks=0;
    void Ok(bool condition,string reason){Require(condition,reason);checks++;}
    var all=ObsAddress44.Registry.Select(x=>x.Glyph).ToArray();
    Ok(all.Length==44&&all.Distinct(StringComparer.Ordinal).Count()==44,"distinct registry");
    Ok(ObsAddress44.CodeOf("n")==0,"zero center");
    Ok(ObsAddress44.CodeOf("m")==13,"band one");
    Ok(ObsAddress44.CodeOf("o")==14&&ObsAddress44.CodeOf("x")==23,"band two");
    Ok(ObsAddress44.CodeOf("y")==24&&ObsAddress44.CodeOf("z")==25,"band three");
    Ok(ObsAddress44.CodeOf("1")==26&&ObsAddress44.CodeOf("9")==34,"digit band");
    Ok(ObsAddress44.CodeOf(".0x")==43,"single terminal glyph");
    foreach(var row in ObsAddress44.Registry)
    {
        Ok(ObsAddress44.ParseDisplayAddress(row.Address)==row.Code,"parse");
        Ok(ObsAddress44.DisplayAddress(row.Code)==row.Address,"display");
        Ok(ObsAddress44.GlyphAt(row.Code)==row.Glyph,"glyph");
        Ok(ObsAddress44.CodeOf(row.Glyph)==row.Code,"code");
    }
    Ok(ObsAddress44.ToKernelTokens(["n","a",".0x"]).SequenceEqual(["0","1","43"]),"substrate token map");
    Ok(ObsAddress44.FromKernelTokens(["0","1","43"]).SequenceEqual(["n","a",".0x"]),"inverse token map");
    Ok(ObsAddress44.Recover(ObsAddress44.Bind(all)).SequenceEqual(all),"all 44 recovered");
    for(int length=1;length<=32;length++)
    {
        var sequence=Enumerable.Range(0,length).Select(i=>all[(i*13+11)%44]).ToArray();
        Ok(ObsAddress44.RecoverFrame(ObsAddress44.MakeFrame(sequence,0),0).SequenceEqual(sequence),"frame "+length);
    }
    Reject(()=>ObsAddress44.CodeOf("0"),"unassigned glyph");
    Reject(()=>ObsAddress44.CodeOf(".0"),".0x is atomic");
    Reject(()=>ObsAddress44.CodeOf("A"),"case");
    Reject(()=>ObsAddress44.ParseDisplayAddress("44"),"invalid bound");
    Reject(()=>ObsAddress44.ParseDisplayAddress("0"),"unformatted display");
    Reject(()=>ObsAddress44.FromKernelTokens(["00"]),"noncanonical floor code");
    Reject(()=>ObsAddress44.FromKernelTokens(["44"]),"reserved");
    Reject(()=>ObsAddress44.FromKernelTokens(["-1"]),"negative");
    return checks+8;
}
static object FrameBenchmark(int count)
{
    string[] glyphs=ObsAddress44.Registry.Select(e=>e.Glyph).ToArray();
    long allocatedBefore=GC.GetTotalAllocatedBytes(true);
    var watch=Stopwatch.StartNew();
    int recovered=0,sequence=0;
    while(recovered<count)
    {
        int take=Math.Min(32,count-recovered);
        var input=Enumerable.Range(recovered,take).Select(i=>glyphs[i%glyphs.Length]).ToArray();
        var decoded=ObsAddress44.RecoverFrame(ObsAddress44.MakeFrame(input,sequence),sequence);
        Require(decoded.SequenceEqual(input),"benchmark exact recovery");
        recovered+=take;sequence++;
    }
    watch.Stop();
    return new {count,frames=sequence,tokensPerSecond=count/watch.Elapsed.TotalSeconds,
        elapsedSeconds=watch.Elapsed.TotalSeconds,allocBytes=GC.GetTotalAllocatedBytes(true)-allocatedBefore};
}
var options=new JsonSerializerOptions{WriteIndented=false};
int assertions=SelfTest();
Console.WriteLine(JsonSerializer.Serialize(new {kind="selftest",assertions,status="PASS",dotnet=Environment.Version.ToString()},options));
string mode=args.FirstOrDefault()??"--help";
if(mode=="--bench44")
{
    int count=args.Length>1?int.Parse(args[1]):20000;
    Require(count>0&&count<=1_000_000,"count 1..1e6");
    _=FrameBenchmark(Math.Min(count,1024)); // warm up
    int runs=args.Length>2?int.Parse(args[2]):5;
    Require(runs is >=1 and <=11,"repetitions");
    var samples=new List<object>();
    var rates=new List<double>();
    for(int i=0;i<runs;i++)
    {
        var result=FrameBenchmark(count);samples.Add(result);
        using var doc=JsonDocument.Parse(JsonSerializer.Serialize(result));
        rates.Add(doc.RootElement.GetProperty("tokensPerSecond").GetDouble());
    }
    rates.Sort();
    Console.WriteLine(JsonSerializer.Serialize(new {kind="bench44",version="OBS44-v1.6",runs,count,
        medianTokensPerSecond=rates[rates.Count/2],samples},options));
}
else if(mode=="--stream")
{
    int count=args.Length>1?int.Parse(args[1]):20000;
    int delay=args.Length>2?int.Parse(args[2]):0;
    _=await ObsStreaming.RunInProcessAsync(Math.Min(count,1024),0);
    var report=await ObsStreaming.RunInProcessAsync(count,delay);
    Console.WriteLine(JsonSerializer.Serialize(new {kind="stream",report},options));
}
else if(mode=="--map44")
    Console.WriteLine(JsonSerializer.Serialize(ObsAddress44.Registry,options));
else Console.WriteLine("Use --bench44 20000 5 or --stream 20000 0 or --map44");
