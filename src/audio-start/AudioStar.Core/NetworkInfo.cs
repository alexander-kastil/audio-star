using System.Net;
using System.Net.Sockets;

namespace AudioStar.Core;

public static class NetworkInfo
{
    public static IPAddress LocalAddressFor(IPAddress remote)
    {
        using var socket = new Socket(remote.AddressFamily, SocketType.Dgram, ProtocolType.Udp);
        socket.Connect(remote, 9);
        return ((IPEndPoint)socket.LocalEndPoint!).Address;
    }

    public static IPAddress PrimaryLocalAddress()
    {
        try
        {
            return LocalAddressFor(IPAddress.Parse("8.8.8.8"));
        }
        catch (SocketException)
        {
            return IPAddress.Loopback;
        }
    }
}
