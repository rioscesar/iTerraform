import os
import subprocess
from celery import Celery
from slackclient import SlackClient

app = Celery('tasks')
app.conf.broker_url = 'redis://localhost:6379/0'
app.conf.result_backend = 'redis://localhost:6379/0'

# instantiate Slack Client
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))

@app.task
def add(channel):
    print 'getting hit', slack_client, channel, os.environ.get('SLACK_BOT_TOKEN')
    dir = os.path.expanduser('~/Automatic/terraform-oci-workshop')
    script = dir + '/env.sh'
    
    output = subprocess.check_output("""
    chmod +x {0}
    . {1}
    terraform init
    terraform plan
    terraform apply -auto-approve
    """.format(script, script), shell=True, executable='/bin/bash', universal_newlines=True, cwd=dir)
    response = output.split('MEAN Stack URL = ')[1]
    print response
    slack_client.api_call('chat.postMessage', channel=channel,
                          text='MEAN Stack URL = {0}'.format(response[0: 26]), as_user=True)
    
