using System;
using Azure.Communication.Identity;

namespace ACS.WPP.Examples
{
    /// <summary>
    /// Example: Channel Registration with Azure Communication Services
    /// </summary>
    public class ChannelRegistration
    {
        public static void Main(string[] args)
        {
            // Replace with your actual connection string
            string connectionString = Environment.GetEnvironmentVariable("ACS_CONNECTION_STRING") 
                ?? "<connection-string>";
            
            var client = new CommunicationIdentityClient(connectionString);
            var identityResponse = client.CreateUser();
            
            Console.WriteLine($"User ID: {identityResponse.Value.Id}");
        }
    }
}
