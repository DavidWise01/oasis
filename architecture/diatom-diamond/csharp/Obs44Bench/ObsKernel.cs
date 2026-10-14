// OASIS OBS C# reference port — exact v0.7 floor + v1.1/v1.2 OBS coordinates.
using System.Globalization;
using System.Numerics;
using System.Text;
using System.Text.RegularExpressions;
namespace Oasis.Obs;
public enum ObsKind { Letter, Number, Special }
public readonly record struct ObsCell(string O, string B, string S);
public sealed record ObsPacket(ObsCell[] Positive, ObsCell[] Negative, int SourceLength);
public sealed record ObsFrame(int Sequence,int Bytes,int Tokens,int Fragments,ObsPacket Source);
public static class ObsKernel
{
    public const string Operators="UUDDLRLRBASS";
    public const int Passes=5, FragmentBytes=1245,MaxTokensPerFrame=32,MaxTokenBytes=4980,MaxFrameBytes=32768;
    public const string FloorVersion="dual5-floor/v0.7";
    public static readonly BigInteger O=BigInteger.Pow(10,10), B=BigInteger.Pow(10,200), S=BigInteger.Pow(10,3000);
    public static readonly BigInteger Capacity=O*B*S;
    private static readonly UTF8Encoding Utf8=new(false,true);
    private static readonly string[] Letters=Enumerable.Range(0,26).Select(i=>$"{(char)('A'+i)}{(char)('a'+i)}{(char)('a'+i)}{(char)('A'+i)}").ToArray();
    private static readonly Regex NumberPattern=new(@"\A(?:0|[1-9][0-9]*)\z",RegexOptions.Compiled|RegexOptions.CultureInvariant);
    public static ObsKind Kind(string value)
    {
        ArgumentNullException.ThrowIfNull(value);
        if(Letters.Contains(value,StringComparer.Ordinal))return ObsKind.Letter;
        if(NumberPattern.IsMatch(value))return ObsKind.Number;
        if(Rune.TryGetRuneAt(value,0,out var scalar)&&scalar.Utf16SequenceLength==value.Length&&
            !Rune.IsLetter(scalar)&&
            Rune.GetUnicodeCategory(scalar) is not (UnicodeCategory.DecimalDigitNumber or UnicodeCategory.LetterNumber or UnicodeCategory.OtherNumber)&&
            !Rune.IsWhiteSpace(scalar))return ObsKind.Special;
        throw new FormatException("Not a canonical OBS token: "+value);
    }
    private static int TypeCode(string value)=>Kind(value) switch
    {
       ObsKind.Letter=>Array.IndexOf(Letters,value),ObsKind.Number=>26,ObsKind.Special=>27,_=>throw new FormatException("Unknown kind")
    };
    private static BigInteger Natural(string text,string label)
    {
        if(string.IsNullOrEmpty(text)||!NumberPattern.IsMatch(text))throw new FormatException($"Noncanonical {label} coordinate");
        return BigInteger.Parse(text,CultureInfo.InvariantCulture);
    }
    public static BigInteger Encode(ObsCell cell)
    {
        var o=Natural(cell.O,"o");var b=Natural(cell.B,"b");var s=Natural(cell.S,"s");
        if(o>=O||b>=B||s>=S)throw new ArgumentOutOfRangeException(nameof(cell));
        return(o*B+b)*S+s;
    }
    public static ObsCell Decode(BigInteger index)
    {
        if(index<0||index>=Capacity)throw new ArgumentOutOfRangeException(nameof(index));
        var s=index%S;var b=(index/S)%B;var o=index/(S*B);
        return new ObsCell(o.ToString(CultureInfo.InvariantCulture),b.ToString(CultureInfo.InvariantCulture),s.ToString(CultureInfo.InvariantCulture));
    }
    public static ObsCell Mirror(ObsCell cell)
    {
        Encode(cell);
        return new ObsCell((O-BigInteger.One-Natural(cell.O,"o")).ToString(CultureInfo.InvariantCulture),
            (B-BigInteger.One-Natural(cell.B,"b")).ToString(CultureInfo.InvariantCulture),
            (S-BigInteger.One-Natural(cell.S,"s")).ToString(CultureInfo.InvariantCulture));
    }
    private static BigInteger BytesToSeed(ReadOnlySpan<byte> bytes)
    {
        if(bytes.Length<1||bytes.Length>FragmentBytes)throw new FormatException("Bad chunk size");
        BigInteger value=new(bytes,isUnsigned:true,isBigEndian:true);
        BigInteger seed=(BigInteger.One<<(bytes.Length*8))+value;
        if(seed>=S)throw new FormatException("s bound exceeded");
        return seed;
    }
    private static byte[] SeedToBytes(BigInteger seed)
    {
        if(seed<=1||seed>=S)throw new FormatException("Invalid seed");
        byte[] raw=seed.ToByteArray(isUnsigned:true,isBigEndian:true);
        if(raw.Length<2||raw.Length>FragmentBytes+1||raw[0]!=1)throw new FormatException("Invalid seed sentinel");
        return raw[1..];
    }
    public static ObsCell[] PackTokens(IEnumerable<string> tokens)
    {
        var output=new List<ObsCell>();
        foreach(var token in tokens)
        {
            int type=TypeCode(token);
            byte[] bytes=Utf8.GetBytes(token);
            for(int start=0,part=0;start<bytes.Length;start+=FragmentBytes,part++)
            {
                if(new BigInteger(part)>=B)throw new ArgumentOutOfRangeException(nameof(tokens));
                int size=Math.Min(FragmentBytes,bytes.Length-start);
                output.Add(new ObsCell(type.ToString(CultureInfo.InvariantCulture),part.ToString(CultureInfo.InvariantCulture),
                    BytesToSeed(bytes.AsSpan(start,size)).ToString(CultureInfo.InvariantCulture)));
            }
        }
        return output.ToArray();
    }
    public static string[] UnpackTokens(IReadOnlyList<ObsCell> cells)
    {
        var tokens=new List<string>();var active=new List<byte>();BigInteger? type=null;BigInteger expected=0;
        void Flush()
        {
            if(type is null)return;
            string value=Utf8.GetString(active.ToArray());
            if(TypeCode(value)!=(int)type.Value)throw new FormatException("Family mismatch");
            tokens.Add(value);active.Clear();type=null;expected=0;
        }
        foreach(var cell in cells)
        {
            Encode(cell);
            var o=Natural(cell.O,"o");var b=Natural(cell.B,"b");var s=Natural(cell.S,"s");
            if(o>27)throw new FormatException("Reserved family");
            if(b==0){Flush();type=o;}
            if(type is null||type!=o||b!=expected)throw new FormatException("Fragment ordering");
            active.AddRange(SeedToBytes(s));expected++;
        }
        Flush();
        if(!PackTokens(tokens).SequenceEqual(cells))throw new FormatException("Noncanonical packet");
        return tokens.ToArray();
    }
    private static string[] Rotate(IReadOnlyList<string> values,int steps)
    {
        int n=values.Count;if(n==0)return [];
        var result=new string[n];int shift=((steps%n)+n)%n;
        for(int i=0;i<n;i++)result[(i+shift)%n]=values[i];
        return result;
    }
    public static string[] Operation(IReadOnlyList<string> values,char op,bool inverse=false)
    {
        var a=values.ToArray();
        switch(op)
        {
            case 'U':return Rotate(a,inverse?-1:1);
            case 'D':return Rotate(a,inverse?1:-1);
            case 'A':return Rotate(a,inverse?-2:2);
            case 'B':Array.Reverse(a);return a;
            case 'L':
            case 'R':
                for(int i=op=='L'?0:1;i+1<a.Length;i+=2)(a[i],a[i+1])=(a[i+1],a[i]);
                return a;
            case 'S':return a;
            default:throw new FormatException("Unknown floor op");
        }
    }
    public static string[] Transform(IEnumerable<string> tokens,bool inverse=false)
    {
        var a=tokens.ToArray();foreach(var token in a)Kind(token);
        for(int pass=0;pass<Passes;pass++)
        {
            IEnumerable<char> ops=inverse?Operators.Reverse():Operators;
            foreach(char op in ops)a=Operation(a,op,inverse);
        }
        return a;
    }
    public static ObsPacket Bind(string[] tokens)
    {
        var plus=PackTokens(Transform(tokens));
        var minus=PackTokens(Transform(tokens.Reverse(),inverse:true));
        return new ObsPacket(plus,minus.Reverse().Select(Mirror).ToArray(),tokens.Length);
    }
    public static string[] Recover(ObsPacket packet)
    {
        var positive=UnpackTokens(packet.Positive);
        var negative=UnpackTokens(packet.Negative.Reverse().Select(Mirror).ToArray());
        var fromPositive=Transform(positive,inverse:true);
        var fromNegative=Transform(negative).Reverse().ToArray();
        if(fromPositive.Length!=packet.SourceLength||!fromPositive.SequenceEqual(fromNegative))
            throw new FormatException("Dual recovery mismatch");
        return fromPositive;
    }
    public static ObsFrame MakeFrame(string[] tokens,int sequence)
    {
        if(sequence<0||tokens.Length is <1 or >MaxTokensPerFrame)throw new ArgumentOutOfRangeException(nameof(tokens));
        int bytes=0;
        foreach(var token in tokens){Kind(token);int n=Utf8.GetByteCount(token);
            if(n is <1 or >MaxTokenBytes)throw new ArgumentOutOfRangeException(nameof(tokens));
            bytes=checked(bytes+n);}
        if(bytes>MaxFrameBytes)throw new ArgumentOutOfRangeException(nameof(tokens));
        var packet=Bind(tokens);
        return new ObsFrame(sequence,bytes,tokens.Length,packet.Positive.Length,packet);
    }
    public static string[] RecoverFrame(ObsFrame frame,int expectedSequence)
    {
        if(frame.Sequence!=expectedSequence||frame.Tokens is <1 or >MaxTokensPerFrame||
           frame.Bytes is <1 or >MaxFrameBytes||frame.Fragments<1||
           frame.Fragments!=frame.Source.Positive.Length||frame.Fragments!=frame.Source.Negative.Length)
             throw new FormatException("Malformed or out-of-order frame");
        var tokens=Recover(frame.Source);
        if(tokens.Length!=frame.Tokens||tokens.Sum(Utf8.GetByteCount)!=frame.Bytes||tokens.Any(t=>Utf8.GetByteCount(t)>MaxTokenBytes))
             throw new FormatException("Frame token/byte count mismatch");
        return tokens;
    }
}