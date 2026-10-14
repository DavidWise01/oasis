// OASIS / KET — OBS44 canonical glyph-address adapter, v1.6.
// Additive only: does not change OBS v1.1 coordinate rules or frozen v0.7 permutations.
using System.Collections.ObjectModel;
using System.Globalization;

namespace Oasis.Obs;

public sealed record Obs44Packet(string Protocol, ObsPacket Source);

public readonly record struct Obs44Entry(int Code, string Address, string Glyph, string Family);

public static class ObsAddress44
{
    public const string Protocol = "OBS44/address-v1.6";
    public const int Count = 44;

    // Address 00 is n. Address 43 is the single atomic glyph ".0x".
    // The spelling and order match the user-supplied registry exactly.
    private static readonly string[] Glyphs =
    [
        "n",                                                   // 00
        "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", // 01-13
        "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", // 14-23
        "y", "z", "1", "2", "3", "4", "5", "6", "7", "8", // 24-33
        "9", ">", "|", ":", "\"", "^", "(", "-", "+", ".0x" // 34-43
    ];
    private static readonly ReadOnlyDictionary<string, int> Codes = new(
        Glyphs.Select((glyph, code) => (glyph, code))
              .ToDictionary(x => x.glyph, x => x.code, StringComparer.Ordinal));
    public static IReadOnlyList<Obs44Entry> Registry { get; } = Array.AsReadOnly(
        Glyphs.Select((glyph, code) => new Obs44Entry(
            code, code.ToString("D2", CultureInfo.InvariantCulture), glyph,
            char.IsAsciiLetter(glyph[0]) && glyph.Length == 1 ? "letter"
                : glyph.Length == 1 && char.IsAsciiDigit(glyph[0]) ? "digit" : "operator"))
        .ToArray());

    static ObsAddress44()
    {
        if (Glyphs.Length != Count || Codes.Count != Count || Glyphs[0] != "n" || Glyphs[43] != ".0x")
            throw new InvalidOperationException("OBS44 registry violates its fixed address map");
    }

    public static int CodeOf(string glyph)
    {
        if (glyph is null || !Codes.TryGetValue(glyph, out int code))
            throw new FormatException("Unregistered OBS44 glyph");
        return code;
    }

    public static string GlyphAt(int code)
    {
        if (code is < 0 or >= Count) throw new ArgumentOutOfRangeException(nameof(code));
        return Glyphs[code];
    }

    public static string DisplayAddress(int code) =>
        (code is >= 0 and < Count ? code : throw new ArgumentOutOfRangeException(nameof(code)))
        .ToString("D2", CultureInfo.InvariantCulture);

    public static int ParseDisplayAddress(string address)
    {
        if (address is null || address.Length != 2 ||
            address[0] is < '0' or > '9' || address[1] is < '0' or > '9')
            throw new FormatException("Display address requires exactly two ASCII digits");
        int code = (address[0] - '0') * 10 + address[1] - '0';
        if (code >= Count) throw new FormatException("OBS44 address outside 00..43");
        return code;
    }

    // IMPORTANT: this is a typed, versioned adapter into the *unchanged* frozen
    // floor. "00" is only a display address; transport uses canonical "0".
    // Thus n -> 0, .0x -> 43. The original lexical family is recovered by
    // the OBS44 dictionary, not inferred from the numeric substrate type.
    public static string[] ToKernelTokens(IEnumerable<string> glyphs) =>
        glyphs.Select(g => CodeOf(g).ToString(CultureInfo.InvariantCulture)).ToArray();

    public static string[] FromKernelTokens(IEnumerable<string> tokens) =>
        tokens.Select(value =>
        {
            if (string.IsNullOrEmpty(value) ||
                !int.TryParse(value, NumberStyles.None, CultureInfo.InvariantCulture, out int code) ||
                code is < 0 or >= Count ||
                value != code.ToString(CultureInfo.InvariantCulture))
                throw new FormatException("Noncanonical OBS44 substrate code");
            return GlyphAt(code);
        }).ToArray();

    public static Obs44Packet Bind(IEnumerable<string> glyphs) =>
        new(Protocol, ObsKernel.Bind(ToKernelTokens(glyphs)));

    public static string[] Recover(Obs44Packet packet)
    {
        if (packet is null || packet.Protocol != Protocol || packet.Source is null)
            throw new FormatException("Invalid OBS44 protocol envelope");
        return FromKernelTokens(ObsKernel.Recover(packet.Source));
    }

    public static ObsFrame MakeFrame(IEnumerable<string> glyphs, int sequence) =>
        ObsKernel.MakeFrame(ToKernelTokens(glyphs), sequence);

    public static string[] RecoverFrame(ObsFrame frame, int sequence) =>
        FromKernelTokens(ObsKernel.RecoverFrame(frame, sequence));
}
