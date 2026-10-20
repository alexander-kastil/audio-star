namespace AudioStar.Speakers.Protocol;

public sealed class SpeakerRequestException(HttpStatusCode statusCode, string operation, string body)
    : Exception($"{operation} failed with HTTP {(int)statusCode}")
{
    public HttpStatusCode StatusCode { get; } = statusCode;
    public string Body { get; } = body;
}
