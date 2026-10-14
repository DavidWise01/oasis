// OASIS OBS44 bounded asynchronous streaming benchmark; additive adapter only.
using System.Diagnostics;
using System.Runtime.CompilerServices;
using System.Text;
using System.Threading.Channels;
namespace Oasis.Obs;
public sealed record ThroughputReport(int Tokens,int Frames,int RecoveredTokens,double ElapsedSeconds,
    double TokensPerSecond,int MaxGeneratedAhead,int ChannelCapacity,string Transport,bool ExactRecovery);
public static class ObsStreaming
{
    private static readonly string[] Specials=["∞","💎","@","|"];
    public static string TokenAt(int i)
    {
        if(i<0)throw new ArgumentOutOfRangeException(nameof(i));
        return (i%4) switch
        {
            0=>LetterAt((i*17+3)%26),
            1=>(((long)i+1)*2_654_435_761L).ToString()+"99999",
            2=>Specials[((i/4)*7+1)%4],
            _=>"0"
        };
    }
    private static string LetterAt(int j)
    {
        char upper=(char)('A'+j),lower=(char)('a'+j);
        return $"{upper}{lower}{lower}{upper}";
    }
    public static async IAsyncEnumerable<string> LazyTokens(int total,
        [EnumeratorCancellation] CancellationToken cancellation=default)
    {
        if(total<0||total>1_000_000)throw new ArgumentOutOfRangeException(nameof(total));
        for(int i=0;i<total;i++)
        {
            cancellation.ThrowIfCancellationRequested();
            yield return TokenAt(i);
            if(i%1024==1023)await Task.Yield();
        }
    }
    public static async IAsyncEnumerable<ObsFrame> EncodeAsync(IAsyncEnumerable<string> source,
        [EnumeratorCancellation] CancellationToken cancellation=default)
    {
        var pending=new List<string>(ObsKernel.MaxTokensPerFrame);
        int bytes=0,seq=0;
        await foreach(var token in source.WithCancellation(cancellation))
        {
            ObsKernel.Kind(token);
            int n=Encoding.UTF8.GetByteCount(token);
            if(n is <1 or >ObsKernel.MaxTokenBytes||n>ObsKernel.MaxFrameBytes)
                throw new ArgumentOutOfRangeException(nameof(source),"Oversized token");
            if(pending.Count>0&&(pending.Count>=ObsKernel.MaxTokensPerFrame||bytes+n>ObsKernel.MaxFrameBytes))
            {
                yield return ObsKernel.MakeFrame(pending.ToArray(),seq++);
                pending.Clear();bytes=0;
            }
            pending.Add(token);bytes+=n;
        }
        if(pending.Count>0)yield return ObsKernel.MakeFrame(pending.ToArray(),seq);
    }
    public static async Task<ThroughputReport> RunInProcessAsync(int count,int consumerDelayMs=0,
        CancellationToken cancellation=default)
    {
        if(count is <1 or >1_000_000)throw new ArgumentOutOfRangeException(nameof(count));
        if(consumerDelayMs is <0 or >100)throw new ArgumentOutOfRangeException(nameof(consumerDelayMs));
        var queue=Channel.CreateBounded<ObsFrame>(new BoundedChannelOptions(1)
        {
            FullMode=BoundedChannelFullMode.Wait,SingleReader=true,SingleWriter=true,AllowSynchronousContinuations=false
        });
        using var linked=CancellationTokenSource.CreateLinkedTokenSource(cancellation);
        var ct=linked.Token;
        int generated=0,recovered=0,frames=0,maxAhead=0;
        var sw=Stopwatch.StartNew();
        async IAsyncEnumerable<string> Counter([EnumeratorCancellation] CancellationToken token)
        {
            await foreach(var item in LazyTokens(count,token))
            {
                Interlocked.Increment(ref generated);
                yield return item;
            }
        }
        var producer=Task.Run(async()=>
        {
            try
            {
                await foreach(var frame in EncodeAsync(Counter(ct),ct))
                    await queue.Writer.WriteAsync(frame,ct);
                queue.Writer.TryComplete();
            }
            catch(Exception ex){queue.Writer.TryComplete(ex);await linked.CancelAsync();throw;}
        },cancellation);
        var consumer=Task.Run(async()=>
        {
            try
            {
                int expected=0;
                await foreach(var frame in queue.Reader.ReadAllAsync(ct))
                {
                    if(consumerDelayMs>0)await Task.Delay(consumerDelayMs,ct);
                    foreach(var token in ObsKernel.RecoverFrame(frame,expected++))
                    {
                        if(token!=TokenAt(recovered))throw new InvalidOperationException("Recovered token mismatch");
                        recovered++;
                    }
                    frames++;
                    maxAhead=Math.Max(maxAhead,Volatile.Read(ref generated)-recovered);
                }
            }
            catch{await linked.CancelAsync();throw;}
        },cancellation);
        await Task.WhenAll(producer,consumer);
        sw.Stop();
        if(recovered!=count)throw new InvalidOperationException("Stream truncated");
        return new ThroughputReport(count,frames,recovered,sw.Elapsed.TotalSeconds,
            count/sw.Elapsed.TotalSeconds,maxAhead,1,"bounded in-process channel",true);
    }
}