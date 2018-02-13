import os
import time
import subprocess
from slackclient import SlackClient
from tasks import add

# starterbot's ID as an env variable
BOT_ID = os.environ.get('BOT_ID')

# constants
AT_BOT = '<@' + BOT_ID + '>'

# instantiate Slack Client
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))


def handle_command(command, channel):
    """
    Receives commands directed at the bot and determines if they are valid commands.
    If so, then acts on teh commands. If not, returns back what it needs for clarification.
    """
    if 'help' in command:
        response = 'Potentially, do you need help deploying your infrastructure on the Oracle Cloud?'
        slack_client.api_call('chat.postMessage', channel=channel, text=response, as_user=True)
    elif 'yes' in command:
        response = 'I can do that! Please provide your tenancy_ocid, compartment_ocid, and user_ocid.'
        slack_client.api_call('chat.postMessage', channel=channel, text=response, as_user=True)
    elif 'tenancy_ocid' in command and 'user_ocid' in command and 'compartment_ocid' in command:
        command = command.split(',')
        tenancy_ocid = command[0].split('=')[1]
        compartment_ocid = command[1].split('=')[1]
        user_ocid = command[2].split('=')[1]

        slack_client.api_call('chat.postMessage', channel=channel, text='Job being processed',
                              as_user=True)
        
        for value in command:
            key = value.split('=')[0]
            val = '"{0}"'.format(value.split('=')[1])
            dir = os.path.expanduser('~/Automatic/terraform-oci-workshop')
            script = dir + '/env.sh'
            cmd = "echo 'export TF_VAR_{0}={1}' >> {2}".format(key, val, script)
            subprocess.call(cmd, shell=True)

        result = add.delay(channel)


def parse_slack_output(slack_rtm_output):
    """
    The Slack Real Time Messaging API is an events firehose.
    This parsing function returns None unless a message is directed at the Bot, based on it's ID.
    """
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                # return text after the @ mention, whitespace removed
                return output['text'].split(AT_BOT)[1].strip().lower(), output['channel']
    return None, None


READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from the firehose
if slack_client.rtm_connect():
    print 'StarterBot connected and running!'
    while True:
        command, channel = parse_slack_output(slack_client.rtm_read())
        if command and channel:
            handle_command(command, channel)
        time.sleep(READ_WEBSOCKET_DELAY)
else:
    print 'Connection failed. Invalid Slack token or bot ID'
