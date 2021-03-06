# -*- coding: utf-8 -*-
"""
A routing layer for the onboarding bot tutorial built using
[Slack's Events API](https://api.slack.com/events-api) in Python
"""
import json
import bot
import convert_units
from flask import Flask, request, make_response, render_template

pyBot = bot.Bot()
slack = pyBot.client

app = Flask(__name__)

#log_file = open("log.txt", "a")

def _event_handler(event_type, slack_event):
    """
    A helper function that routes events from Slack to our Bot
    by event type and subtype.

    Parameters
    ----------
    event_type : str
        type of event recieved from Slack
    slack_event : dict
        JSON response from a Slack reaction event

    Returns
    ----------
    obj
        Response object with 200 - ok or 500 - No Event Handler error

    """

    log_file = open("log.txt", "a")
    response = ''
    bot_action = None
    team_id = slack_event["team_id"]

    log_file.write("_______________________" + "\n")
    #print "event_type", event_type
    #print "event", slack_event
    if event_type == "message":
        #print "team_id", team_id
        channel = slack_event["event"].get("channel")
        #print "channel", channel
        username = slack_event["event"].get("username", None)
        #print "username", username
        msg = slack_event["event"].get("text", "")
        if username == 'unitsbot':
            print 'unitsbot_msg: ', msg
            log_file.write("unitsbot_msg: " + msg.encode('utf8') + "\n")
        else:
            print 'msg: ', msg
            log_file.write("msg: " + msg.encode('utf8') + "\n")
        if msg:
            msg = msg.lower()

        log_file.write("team_id: " + team_id + "\n")
        log_file.write("channel: " + channel + "\n")

        if channel=="D53NMCT0A" and msg.startswith("\\"):  # DM from james_
            cmd, arg1, arg2 = msg[1:].split()
            if cmd=="delete":
                channel = arg1.upper()
                #print "channel", channel
                ts = arg2
                #print "ts_real", ts
                bot_action = pyBot.delete_message(team_id, channel, ts)
            if cmd=="msg":
                channel = arg1.upper()
                response = arg
                ts = None
                bot_action = pyBot.send_message(response, team_id, channel, username, ts)

        else:  # convert mention(s) of units
            atunitsbot = "<@u52m3ut7a>" #TODO: hardcoded for now, automatically get bot's user_id for this team_id
            if msg.startswith(atunitsbot): # message direct to unitsbot
                #print "@unitsbot mention"
                response = convert_units.pint_convert(msg.replace(atunitsbot, ''))
            else:
                response = convert_units.convert_units(msg)

            ts = slack_event["event"].get("ts")
            log_file.write("ts: "+ ts + "\n")
            if(response and username!=pyBot.name):
                bot_action = pyBot.send_message(response, team_id, channel, username, ts)


        log_file.write('response: ' + response.encode('utf8') + '\n')
        log_file.write('event_type: '+event_type+': ')
        log_file.write(json.dumps(slack_event))
        log_file.write('\n')
        log_file.write('bot_action: ')
        log_file.write(json.dumps(bot_action))
        log_file.write('\n')
        return make_response("response processed", 200,)
    # ================ Team Join Events =============== #
    # When the user first joins a team, the type of event will be team_join
    # if event_type == "team_join":
    #     user_id = slack_event["event"]["user"]["id"]
    #     # Send the onboarding message
    #     pyBot.onboarding_message(team_id, user_id)
    #     return make_response("Welcome Message Sent", 200,)
    #
    # # ============== Share Message Events ============= #
    # # If the user has shared the onboarding message, the event type will be
    # # message. We'll also need to check that this is a message that has been
    # # shared by looking into the attachments for "is_shared".
    # elif event_type == "message" and slack_event["event"].get("attachments"):
    #     user_id = slack_event["event"].get("user")
    #     if slack_event["event"]["attachments"][0].get("is_share"):
    #         # Update the onboarding message and check off "Share this Message"
    #         pyBot.update_share(team_id, user_id)
    #         return make_response("Welcome message updates with shared message",
    #                              200,)
    #
    # # ============= Reaction Added Events ============= #
    # # If the user has added an emoji reaction to the onboarding message
    # elif event_type == "reaction_added":
    #     user_id = slack_event["event"]["user"]
    #     # Update the onboarding message
    #     pyBot.update_emoji(team_id, user_id)
    #     return make_response("Welcome message updates with reactji", 200,)
    #
    # # =============== Pin Added Events ================ #
    # # If the user has added an emoji reaction to the onboarding message
    # elif event_type == "pin_added":
    #     user_id = slack_event["event"]["user"]
    #     # Update the onboarding message
    #     pyBot.update_pin(team_id, user_id)
    #     return make_response("Welcome message updates with pin", 200,)
    #
    # # ============= Event Type Not Found! ============= #
    # # If the event_type does not have a handler
    message = "You have not added an event handler for the %s" % event_type
    # Return a helpful error message
    return make_response(message, 200, {"X-Slack-No-Retry": 1})


@app.route("/install", methods=["GET"])
def pre_install():
    """This route renders the installation page with 'Add to Slack' button."""
    # Since we've set the client ID and scope on our Bot object, we can change
    # them more easily while we're developing our app.
    client_id = pyBot.oauth["client_id"]
    scope = pyBot.oauth["scope"]
    # Our template is using the Jinja templating language to dynamically pass
    # our client id and scope
    return render_template("install.html", client_id=client_id, scope=scope)


@app.route("/thanks", methods=["GET", "POST"])
def thanks():
    """
    This route is called by Slack after the user installs our app. It will
    exchange the temporary authorization code Slack sends for an OAuth token
    which we'll save on the bot object to use later.
    To let the user know what's happened it will also render a thank you page.
    """
    # Let's grab that temporary authorization code Slack's sent us from
    # the request's parameters.
    code_arg = request.args.get('code')
    # The bot's auth method to handles exchanging the code for an OAuth token
    pyBot.auth(code_arg)
    return render_template("thanks.html")


@app.route("/listening", methods=["GET", "POST"])
def hears():
    """
    This route listens for incoming events from Slack and uses the event
    handler helper function to route events to our Bot.
    """

    slack_event = json.loads(request.data)


    # ============= Slack URL Verification ============ #
    # In order to verify the url of our endpoint, Slack will send a challenge
    # token in a request and check for this token in the response our endpoint
    # sends back.
    #       For more info: https://api.slack.com/events/url_verification
    if "challenge" in slack_event:
        return make_response(slack_event["challenge"], 200, {"content_type":
                                                             "application/json"
                                                             })

    # ============ Slack Token Verification =========== #
    # We can verify the request is coming from Slack by checking that the
    # verification token in the request matches our app's settings
    if pyBot.verification != slack_event.get("token"):
        message = "Invalid Slack verification token: %s \npyBot has: \
                   %s\n\n" % (slack_event["token"], pyBot.verification)
        # By adding "X-Slack-No-Retry" : 1 to our response headers, we turn off
        # Slack's automatic retries during development.
        make_response(message, 403, {"X-Slack-No-Retry": 1})

    # ====== Process Incoming Events from Slack ======= #
    # If the incoming request is an Event we've subcribed to
    if "event" in slack_event:
        # don't process events that took place >=1 minute ago
        retry_num = request.headers.get("X-Slack-Retry-Num")
        #print "retry_number", retry_num
        if retry_num > 1:
            return make_response("[NO EVENT IN SLACK REQUEST] These are not the droids\
                                 you're looking for.", 404, {"X-Slack-No-Retry": 1})
        else: # first or second time this request has been sent (basically real-time)
            event_type = slack_event["event"]["type"]
            #print event_type
            #print slack_event
            # Then handle the event by event_type and have your bot respond
            return _event_handler(event_type, slack_event)
    # If our bot hears things that are not events we've subscribed to,
    # send a quirky but helpful error response
    return make_response("[NO EVENT IN SLACK REQUEST] These are not the droids\
                         you're looking for.", 404, {"X-Slack-No-Retry": 1})


if __name__ == '__main__':
    app.run(debug=True)
