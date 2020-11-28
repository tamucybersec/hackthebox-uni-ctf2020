# Solution

We find documentation that outlines how to invite a discord bot to your server:

![Discord Bot Invite Link Schema](imgs/htbxuni_ai_bot_invite_link.png)

In order to move further we need the client ID of the discord bot. If we look in the #uni-ctf-misc-ai-challenge channel, we see that the bot is online, and we can copy it's id:

![Discord Bot Client ID](imgs/htbxuni_ai_bot_client_id.png)

We put these two together and we the following link allows us to invite the bot to servers we have high privileges to:

https://discord.com/oauth2/authorize?client_id=764609448089092119&scope=bot

We successfully add the bot to server:

![Discord Bot Server Join](imgs/htbxuni_ai_server_join.png)

We attempt to shutdown and it fails because we are not an "Administrator":

![Shutdown Attempt Fail](imgs/htbxuni_ai_shutdown_attempt_fail.png)

We create a role named "Administrator" and add ourselves to it. Privileges are irrelevant, all that matter is that the name is named exactly as so. We try again, and we successfully get the flag:

![Shutdown Attempt Success](imgs/htbxuni_ai_flag.png)
