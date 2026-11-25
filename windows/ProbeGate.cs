using System;
using System.Text.Json;
using System.Text.RegularExpressions;

namespace SefaXTV.WindowsLab;

// Host side checks are independent of the HTML. Only own packaged LAB fixture.
internal sealed class ProbeGate
{
    public const string Origin = "https://appassets.androidplatform.net";
    public const string App = Origin + "/assets/index.html";
    public const string Fixture = Origin + "/assets/lab-player.html";
    public const string Protocol = "sefaxtv-probe-v1";
    private long high, seq, counter;
    private string? token, url;
    private object? bound;
    private double media;
    private bool ready;
    public void SetReady(bool value) { ready = value; if (!value) Clear(); }
    public void NewDocument() { ready = false; high = 0; Clear(); }
    private void Clear() { seq = counter = 0; token = url = null; bound = null; media = -1; }
    public bool Start(long s, string? t, string? u)
    {
        if (!ready || s <= high || s > 9007199254740991L || t is null || !Regex.IsMatch(t, "\\A[a-f0-9]{32}\\z") || u is null) return false;
        string prefix = Fixture + "#seq=" + s.ToString(System.Globalization.CultureInfo.InvariantCulture) + "&token=" + t + "&mode=";
        if (u != prefix + "play" && u != prefix + "stall" && u != prefix + "ready") return false;
        Clear(); high = seq = s; token = t; url = u; return true;
    }
    public bool Bind(object frame, string actualUrl)
    {
        if (!ready || seq == 0 || bound != null || actualUrl != url) return false;
        bound = frame; return true;
    }
    public bool IsBound(object frame) => ReferenceEquals(bound, frame);
    public void InvalidateFrame(object frame) { if (IsBound(frame)) Clear(); }
    public bool Stop(long s, string? t) { if (!ready || seq == 0 || seq != s || token != t) return false; Clear(); return true; }
    public bool Proof(object frame, string actualUrl, JsonElement d)
    {
        try
        {
            if (!ready || seq == 0 || !IsBound(frame) || actualUrl != url || d.GetProperty("protocol").GetString() != Protocol || d.GetProperty("type").GetString() != "video:advanced" || d.GetProperty("seq").GetInt64() != seq || d.GetProperty("token").GetString() != token || d.GetProperty("url").GetString() != url) return false;
            long c = d.GetProperty("counter").GetInt64(), frames = d.GetProperty("frameDelta").GetInt64();
            double mt = d.GetProperty("mediaTime").GetDouble(), delta = d.GetProperty("delta").GetDouble();
            string? method = d.GetProperty("method").GetString();
            if (c <= counter || c >= 1000000000 || !double.IsFinite(mt) || mt <= media || mt <= 0 || mt > 1e9 || !double.IsFinite(delta) || delta <= 0 || delta > mt + .000001) return false;
            if (method == "frames") { if (frames < 1 || frames >= 1000000000 || delta < .16) return false; }
            else if (method == "time") { if (frames != 0 || delta < .25) return false; }
            else return false;
            counter = c; media = mt; return true;
        }
        catch (Exception e) when (e is InvalidOperationException or KeyNotFoundException or FormatException or OverflowException) { return false; }
    }
    public static bool ResourceAllowed(string url, string method)
    {
        if (method != "GET" || !Uri.TryCreate(url, UriKind.Absolute, out var u) || u.Scheme != "https" || !u.IsDefaultPort || u.UserInfo.Length != 0 || u.Query.Length != 0) return false;
        if (u.Host == "appassets.androidplatform.net") return u.AbsolutePath is "/assets/index.html" or "/assets/lab-player.html";
        return u.Host == "sedathut-sys.github.io" && Regex.IsMatch(u.AbsolutePath, "\\A/sefaxtv/catalog/(latest|v[1-9][0-9]{0,6})\\.json\\z");
    }
}
