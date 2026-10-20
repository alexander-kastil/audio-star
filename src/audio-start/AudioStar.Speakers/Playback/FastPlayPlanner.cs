namespace AudioStar.Speakers.Playback;

internal sealed record FastPlayPlan(
    IReadOnlyList<int> Initial,
    IReadOnlyList<IReadOnlyList<int>> TailChunks,
    IReadOnlyList<IReadOnlyList<int>> HeadChunks);

internal static class FastPlayPlanner
{
    public const int ChunkSize = 50;
    public const int AppendLimit = 500;
    public const int MaxHead = 250;

    public static FastPlayPlan Plan(int count, int startIndex)
    {
        if (count <= 0)
        {
            return new FastPlayPlan([], [], []);
        }
        var index = Math.Clamp(startIndex, 0, count - 1);
        if (count == 1)
        {
            return new FastPlayPlan([0], [], []);
        }
        var nextIndex = index < count - 1 ? index + 1 : 0;
        IReadOnlyList<int> initial = nextIndex == 0 ? [index] : [index, index + 1];

        var headCount = Math.Min(index, MaxHead);
        var tailCount = Math.Max(0, count - index - 2);
        if (tailCount + headCount > AppendLimit)
        {
            tailCount = AppendLimit - headCount;
        }
        else
        {
            headCount = Math.Min(index, AppendLimit - tailCount);
        }

        var tail = Chunk(Enumerable.Range(index + 2, tailCount));
        var head = Chunk(Enumerable.Range(index - headCount, headCount));
        head.Reverse();
        return new FastPlayPlan(initial, tail, head);
    }

    private static List<IReadOnlyList<int>> Chunk(IEnumerable<int> indices)
    {
        return [.. indices.Chunk(ChunkSize).Select(c => (IReadOnlyList<int>)c)];
    }
}
