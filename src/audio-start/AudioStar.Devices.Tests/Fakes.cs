using AudioStar.Core;
using NSubstitute;

namespace AudioStar.Devices.Tests;

internal static class Fakes
{
    public static SpeakerInfo Info(string id, string name, string ip, string model = "WiiM Amp")
    {
        return new SpeakerInfo(id, name, ip, 59152, model, "Linkplay.5.2.830149");
    }

    public static ISpeakerSession Session(SpeakerInfo info, ISpeakerController? controller = null, string? leaderId = null, params string[] followerIds)
    {
        var session = Substitute.For<ISpeakerSession>();
        session.Info.Returns(info);
        session.Controller.Returns(controller ?? Substitute.For<ISpeakerController>());
        session.LeaderId.Returns(leaderId);
        session.FollowerIds.Returns(followerIds);
        session.State.Returns(PlaybackState.Empty with { Volume = 40, Muted = true });
        return session;
    }

    public static ISpeakerHub Hub(params ISpeakerSession[] sessions)
    {
        var hub = Substitute.For<ISpeakerHub>();
        hub.Speakers.Returns(sessions);
        hub.Find(Arg.Any<string>()).Returns(call => sessions.FirstOrDefault(s => s.Info.Id == call.Arg<string>()));
        return hub;
    }

    public static ISpeakerController Controller(IDictionary<string, string> replies)
    {
        var controller = Substitute.For<ISpeakerController>();
        controller.SendCommandAsync(Arg.Any<string>(), Arg.Any<CancellationToken>())
            .Returns(call => Task.FromResult(replies.TryGetValue(call.Arg<string>(), out var reply) ? reply : "Failed"));
        controller.PostCommandAsync(Arg.Any<string>(), Arg.Any<string>(), Arg.Any<CancellationToken>()).Returns("OK");
        return controller;
    }
}
