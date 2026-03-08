using System;
using System.Threading.Tasks;
using Azure.Communication.WhatsApp;

namespace ACS.WPP.Examples
{
    /// <summary>
    /// Example: Sending Media Messages (Images, Videos, Documents)
    /// </summary>
    public class SendMediaMessage
    {
        public static async Task Main(string[] args)
        {
            string connectionString = Environment.GetEnvironmentVariable("ACS_CONNECTION_STRING") 
                ?? "<connection-string>";
            
            var client = new WhatsAppClient(connectionString);

            try
            {
                await client.SendMediaMessageAsync(new MediaMessageOptions
                {
                    From = Environment.GetEnvironmentVariable("BUSINESS_NUMBER") ?? "<business-number>",
                    To = Environment.GetEnvironmentVariable("USER_NUMBER") ?? "<user-number>",
                    MediaUrl = "https://example.com/image.png",
                    Caption = "Here is your requested image"
                });

                Console.WriteLine("Media message sent successfully!");
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine($"Error sending media message: {ex.Message}");
            }
        }
    }
}
