import datetime
import logging

import azure.functions as func
from ..SharedCode.sharedCode import get_accounts_for_teams, get_opportunities_for_channels,get_projects_for_channels
from ..SharedCode.sharedCode import make_group_for_account,create_teams_for_given_group_id,create_account_counterpart_teams
from ..SharedCode.sharedCode import create_channel, create_channels_for_projects, create_channels_for_opportunities
from ..SharedCode.sharedCode import get_real_opportunities_for_channels, create_channels_for_real_opportunities

def main(mytimer: func.TimerRequest) -> None:


    real_opportunity_channels = create_channels_for_real_opportunities()
    