import requests
import json
import urllib.parse
import msal
import pandas as pd
import time
import logging
import urllib.parse
from requests.auth import HTTPBasicAuth
from requests_ntlm import HttpNtlmAuth
import random
from unidecode import unidecode
import re
import os 
import sys 
import time
# logging.basicConfig(level=logging.DEBUG,format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

# Exact credentials
usernam1 = os.environ['username1']
password1 = os.environ['password1']
SERVICE_URL = os.environ['SERVICE_URL']
#usernam1,password1
headers={"Accept":"application/json"}
header_post = {"X-HTTP-Method":"MERGE","Accept":"application/json","Content-type":"application/json"}
auth=HttpNtlmAuth(usernam1,password1)

# Teams application credentials/Azure AD
client_id = os.environ['client_id'] 
tenant_id = os.environ['tenant_id'] 
secret_app = os.environ['secret_app']
service_graph_url = os.environ['service_graph_url']

config = {"authority": "https://login.microsoftonline.com/a71bd01c-aa93-446c-849f-a2c5fe237ffb",
        "client_id": client_id ,
        "scope":"https://graph.microsoft.com/.default",
        "secret":secret_app,
        "grant_type":"client_credentials"
        }

app = msal.ConfidentialClientApplication(
    config["client_id"], authority=config["authority"],
    client_credential=config["secret"],
    )

result = app.acquire_token_for_client(config['scope'])['access_token']

headers_teams = {"Authorization": "Bearer {}".format(result)}

headers_teams['Accept'] = "application/json"

headers_teams['Content-type'] = "application/json"

def get_header_teams():


    client_id = "eadd66a6-4701-4198-91f5-bd61c89e7c21"
    tenant_id = "a71bd01c-aa93-446c-849f-a2c5fe237ffb"
    secret_app= "r4HD1dkLLVmw/EX6e8GkP/H:V].eaRz/"
    service_graph_url = "https://graph.microsoft.com/v1.0/"

    config = {"authority": "https://login.microsoftonline.com/a71bd01c-aa93-446c-849f-a2c5fe237ffb",
        "client_id": client_id ,
        "scope":"https://graph.microsoft.com/.default",
        "secret":secret_app,
        "grant_type":"client_credentials"
        }


    #First we need to get token

    app = msal.ConfidentialClientApplication(
        config["client_id"], authority=config["authority"],
        client_credential=config["secret"],  
        )


    result = app.acquire_token_for_client(config['scope'])['access_token']

    headers_teams = {"Authorization": "Bearer {}".format(result)}

    headers_teams['Accept'] = "application/json"

    headers_teams['Content-type'] = "application/json"
    return headers_teams






def get_accounts_for_teams():
    '''
    This function returns the list of account that we need to create TEAMS for. 
    '''
    # accountt_url_test = "https://pqrtest.2exact.com/Services/Exact.Entity.REST.svc/Account?$filter=(CustomerType eq 'P' or CustomerType eq'C') and (TextFreeField29 eq null)&$select=AccountName,ID,AccountCode,TextFreeField29,TextFreeField30"
    accountt_url_test = SERVICE_URL + "Account?$filter=(CustomerType eq 'P' or CustomerType eq'C') and (TextFreeField29 eq null)&$select=AccountName,ID,AccountCode,TextFreeField29,TextFreeField30&$top=99"

    accounts_for_teams = requests.get(accountt_url_test,auth=HttpNtlmAuth(usernam1,password1), headers=headers)
    results=[]
    if accounts_for_teams.ok == True:
        if len(accounts_for_teams.json()['d']['results']) != 0:
            
            results = accounts_for_teams.json()['d']['results']

            while ("__next" in accounts_for_teams.json()['d'].keys()):
                print("New chunk of accounts")
                
                # Here we need to manually take skiptoken from returned _next url,
                # and append it to the original accountt_url_test link 
                
                #take the linke from __next parameter:
                link_ = accounts_for_teams.json()['d']['__next']
                
                skip_token_with_add = link_.split("TextFreeField30")[1]

                print("Skip token with add: ",skip_token_with_add)
                
                if skip_token_with_add[:5] != "&$top":
                    skip = skip_token_with_add.split("&$")[1]
                    
                    
                    next_chunk_url = accountt_url_test + "&$" + skip
                    print("Next chunk url: ",next_chunk_url)
                else:
                    
                    next_chunk_url = accountt_url_test[:-8] + skip_token_with_add
                    
                    
                    print("Next chunk url: ",next_chunk_url)
                


                accounts_for_teams = requests.get(next_chunk_url,auth=HttpNtlmAuth(usernam1,password1), headers=headers)
                
                results_tmp = accounts_for_teams.json()['d']['results']
                results.extend(results_tmp)
                
                if len(results)>300:
                    break
                
        else:
            pass

    return results   



    
def get_opportunities_for_channels():    
    '''
    This function returns opportunities that we need to create channels for.
    
    ParentProject eq null - this is the key for extracting the opportunities
    TextFreeField1 eq null - this is the key for extracting those without channel in TEAMS
    startswith(ProjectNumber,'VK') eq true) , VK - this is the key verkoop .....
    
    YesNoFreeField1 eq true - this is the key, if the opportunity really needs to have channel in Teams
    '''
    
    opportunity_url = SERVICE_URL + "Project?$filter=(ParentProject eq null and YesNoFreeField1 eq true and TextFreeField1 eq null and startswith(ProjectNumber,'VK') eq true)&$top=99"
    
    opportunities_for_channels = requests.get(opportunity_url,auth=HttpNtlmAuth(usernam1,password1), headers=headers)

    results=[]
    if opportunities_for_channels.ok == True:
        if len(opportunities_for_channels.json()['d']['results']) != 0:
            results = opportunities_for_channels.json()['d']['results']

            while ("__next" in opportunities_for_channels.json()['d'].keys()):
                print("New chunk of opportunities")
                
                link_ = opportunities_for_channels.json()['d']['__next']
                
                skip_token_with_add = link_.split("true)")[1]

                print("Skip token with add: ",skip_token_with_add)
                
                if skip_token_with_add[:5] != "&$top":
                    skip = skip_token_with_add.split("&$")[1]
                    
                    
                    next_chunk_url = opportunity_url + "&$" + skip
                    print("Next chunk url: ",next_chunk_url)
                else:
                    
                    next_chunk_url = opportunity_url[:-8] + skip_token_with_add

                opportunities_for_channels = requests.get(next_chunk_url,auth=HttpNtlmAuth(usernam1,password1), headers=headers)
                
                results_tmp = opportunities_for_channels.json()['d']['results']
                results.extend(results_tmp)
        else:
            pass
               
    return results


def get_projects_for_channels():
    
    '''
    This function returns list of projects, that we need to create channels for:
    
    - ParentProject ne null - this is the key for extracting the projects (child projects)
    - TextFreeField1 eq null - this is the key for extracting those without channel in TEAMS
    - startswith(ProjectNumber,'VK') eq true) , VK - this is the key verkoop .....
    - YesNoFreeField1 eq true , this is the key to extract only those projects for which we need a channel
      in TEAMS (explicitly setup by user) ???! Try to change it
      
    '''

    projects_url = SERVICE_URL + "Project?$filter=(ParentProject ne null and YesNoFreeField1 eq true and TextFreeField1 eq null and startswith(ProjectNumber,'VK') eq true)&$top=99"

    projects_for_channels = requests.get(projects_url,auth=HttpNtlmAuth(usernam1,password1), headers=headers)

    results=[]
    if projects_for_channels.ok == True:
        if len(projects_for_channels.json()['d']['results']) != 0:
            results = projects_for_channels.json()['d']['results']
            results

            while ("__next" in projects_for_channels.json()['d'].keys()):
                print("New chunk of opportunities")
                
                link_ = projects_for_channels.json()['d']['__next']
                
                skip_token_with_add = link_.split("true)")[1]

                print("Skip token with add: ",skip_token_with_add)
                
                if skip_token_with_add[:5] != "&$top":
                    skip = skip_token_with_add.split("&$")[1]
                    next_chunk_url = projects_url + "&$" + skip
                    print("Next chunk url: ",next_chunk_url)
                else:
                    next_chunk_url = projects_url[:-8] + skip_token_with_add
                

                projects_for_channels = requests.get(next_chunk_url,auth=HttpNtlmAuth(usernam1,password1), headers=headers)
                results_tmp = projects_for_channels.json()['d']['results']
                results.extend(results_tmp)
        else:
            pass
    
    return results


def take_all_groups(ht):
    '''
    Retourns all Office 365 groups from Tenenat
    '''
    results = []
    # ht = get_header_teams()

    # groups = requests.get(service_graph_url+"groups",headers=headers_teams)
    groups = requests.get(service_graph_url+"groups",headers=ht)

    if groups.ok == True:
        results = groups.json()['value']
        
        while("@odata.nextLink" in groups.json().keys()):
            
            link_ = groups.json()['@odata.nextLink']
            
            # groups = requests.get(link_, headers=headers_teams)
            
            groups = requests.get(link_, headers=ht)
            
            if groups.ok == True:
                tmp_results = groups.json()['value']
     
                results.extend(tmp_results)
            else:
                pass
            
    return results




def make_group_for_account(ht,account,list_of_all_group_names=[]):
    
    '''This function will create a group in Office365, based on account, and return response object
    
    Example of account format :
    
    account = {'__metadata': {'id': "https://pqrtest.2exact.com/services/Exact.Entity.REST.svc/Account(guid'*****-****-****-92ad-65d3f5fa2b26')",
                'uri': "https://pqrtest.2exact.com/services/Exact.Entity.REST.svc/Account(guid'ee310e6f-****-4949-****-65d3f5fa2b26')",
                'type': 'Exact.Metadata.Entity.Account'},
                'AccountCode': '              500050',
                'ID': 'ee310e6f-dbdc-4949-92ad-65d3f5fa2b26',
                'AccountName': 'Gemeente Boxmeer 2',
                'TextFreeField9': None}
    '''
    
    
    acc_name = account['AccountName']
    
    it_1 = re.sub("\(|\)|\,|\[|\]|\/|\:|\®|\"|\@|\©|\#|\;|\$|\.|\^|\%","",acc_name)
    it_1 = re.sub("'"," ",it_1)
    unaccented_name = unidecode(it_1)
    unaccented_name
    
    description = unaccented_name
    displayName = unaccented_name + "-" + account['AccountCode'].strip()
    
    
    
    #     description = account['AccountName']
    #     displayName = account['AccountName'] + "-" + account['AccountCode'].strip()
        
    #     mailNickname = account['AccountName'].replace(" ","_") + "_" + str(random.randrange(1,99))
    mailNickname = unaccented_name.replace(" ","_") + "_" + str(random.randrange(1,99))


    group_model = {
        "description": description,
        "displayName": displayName,
        "groupTypes": ["Unified"],
        "mailEnabled": True,
        "mailNickname": mailNickname,
        "visibility": "Private",
        "securityEnabled": False,
        "owners@odata.bind": [
            "https://graph.microsoft.com/v1.0/users/{}".format("85655eed-a5e4-48a3-ae85-7397a49af697")
             # note System ID is: "85655eed-a5e4-48a3-ae85-7397a49af697" - needs license for Office 365
            #Petar ID is: "b2faa591-e6f4-48fa-986d-a0cf3710d32c"
        ]
        }

    # ht = get_header_teams()

    # new_group = requests.post(service_graph_url+'groups',data=json.dumps(group_model),headers=headers_teams)
    new_group = requests.post(service_graph_url+'groups',data=json.dumps(group_model),headers=ht)
   
    return new_group



def create_teams_for_given_group_id(ht,group_id):
    team_object = { 
                "visibility":"private",
                "memberSettings": {
                "allowCreateUpdateChannels": True
                },
                "messagingSettings": {
                "allowUserEditMessages": True,
                "allowUserDeleteMessages": True
                },
                "funSettings": {
                "allowGiphy": True,
                "giphyContentRating": "strict"
                }
                }
    
    create_team_url =service_graph_url + "groups/{}/team".format(group_id)

    # For every account in 'results', we need to extract AccountCode, 
    # ht = get_header_teams()
    # new_team = requests.put(create_team_url, data=json.dumps(team_object),headers=headers_teams)
    new_team = requests.put(create_team_url, data=json.dumps(team_object),headers=ht)

    return new_team


def create_account_counterpart_teams():
    
    '''
    This function will create one TEAM for every account in Exact.
    First, it creates Office365 group in Azure AD, assigning SynergyTeams (system account) as group owner.
    For newly created group, it will also create the TEAM.
    After team creation, it will update "TextFreeField9" field with team id. 
    Keeping information about the team id is necessary, since we need to use that information, 
    every time we need to make a chanel for opportunity or project.    
    '''
    
    accounts = get_accounts_for_teams() # take all accounts without teams counterparts

    print(accounts)
    ht = get_header_teams()

    logging.info(accounts)

    all_groups = take_all_groups(ht)
    df_groups = pd.DataFrame(all_groups)

    try:
        group_name_list = df_groups['displayName'].tolist()
    except:  
        group_name_list = []
    
    if len(accounts) == 0:
        logging.info("No new accounts")
        return "No new accounts"
    
    new_group_id = "error"
    new_team_url = "error"
    
    for ind,account in enumerate(accounts):
        # Here we are trying to discover if the account already has an group (just in case)
        acc_name = account['AccountName']
        it_1 = re.sub("\(|\)|\,|\[|\]|\/|\:|\®|\"|\@|\©|\#|\;|\$|\.|\^|\%","",acc_name)
        it_1 = re.sub("'"," ",it_1)
        unaccented_name = unidecode(it_1)
        tmp_account_name = unaccented_name + "-" + account['AccountCode'].strip()

        if tmp_account_name in group_name_list:
            #if the group with specific name already exists, the new one will not be created
            
            link_to_update_account = account['__metadata']['id']
            new_group_id = df_groups.loc[df_groups['displayName']==tmp_account_name,'id'].to_numpy()[0]
            new_team = create_teams_for_given_group_id(ht,new_group_id)
            print("Comment from team creation: ", new_team.reason)

            if new_team.ok == True: # the teams is successfully created, update TextFreeField9 with group/teams ID
                new_team_url = new_team.json()['webUrl']
                updated_account = requests.post(link_to_update_account,auth=HttpNtlmAuth(usernam1,password1), data=json.dumps({"TextFreeField29":"{}".format(new_group_id),"TextFreeField30":"{}".format(new_team_url)}),headers=header_post)          
            logging.info(" AccountID: {}, AccountName: {}, CreatedGroupID: {}, TeamUrl: {}".format(account['ID'],account['AccountName'],new_group_id,new_team_url))
        
            continue
            
        link_to_update_account = account['__metadata']['id']
        
        new_group = make_group_for_account(ht,account)

        if new_group.ok == True:

            new_group_id = new_group.json()['id']
            time.sleep(1) 
            new_team = create_teams_for_given_group_id(ht,new_group_id)

            if new_team.ok == True: # the teams is successfully created, update TextFreeField9 with group/teams ID
                new_team_url = new_team.json()['webUrl']
                
                updated_account = requests.post(link_to_update_account,auth=HttpNtlmAuth(usernam1,password1), data=json.dumps({"TextFreeField29":"{}".format(new_group_id),"TextFreeField30":"{}".format(new_team_url)}),headers=header_post)
                print("Account updated: ",updated_account.ok )

                time.sleep(8)
                        
        logging.info(" AccountID: {}, AccountName: {}, CreatedGroupID: {}, TeamUrl: {}".format(account['ID'],account['AccountName'],new_group_id,new_team_url))
        


def create_channel(ht,channel_name, group_id):
    
    '''
    Returns channel object (response)
    
    Parameters:
    
    channel_name (str) - Display name of the channel in Teams
    group_id (str) - Group/Teams ID, in which we are creating the channel
    
    '''
    
    
    channel_object = {
      "displayName": channel_name,
      "description": "Default description",
      "membershipType": "private"
        }
 
    create_channel_url =service_graph_url +  "teams/{}/channels".format(group_id)

    # For every account in 'results', we need to extract AccountCode, 
    # new_channel = requests.post(create_channel_url, data=json.dumps(channel_object),headers=headers_teams)
    new_channel = requests.post(create_channel_url, data=json.dumps(channel_object),headers=ht)

    return new_channel



def create_channels_for_projects():
    '''
    Creates channel for all projects
    '''

    channel_name = 'Error'
    accoun_reference = "Error"
    new_channel_created = "Error"
    project_updated = "Error"
    
    # Get the list of all projects
    
    projects_for_channels = get_projects_for_channels()
    
    print("Projects are: ", projects_for_channels)
    
    if len(projects_for_channels) == 0:
        return "No projects for update"

    ht = get_header_teams()

    # Itterate through the list of projects
    for project in projects_for_channels:
        
        project_url = project['__metadata']['id'] 
        
        project_number = project['ProjectNumber']
        
        #limit description project to 30 character
        
        descr = project['Description'][:20]
    
        it_1 = re.sub("\(|\)|\,|\[|\]|\/|\:|\®|\"|\@|\©|\#|\;|\$|\.|\^|\%","",descr)
        it_1 = re.sub("'"," ",it_1)
        description_cleared = unidecode(it_1)
             
        # Create channel name, according to the naming convention
        channel_name = "PR" + project['ParentProject'][-5:] + "-" + description_cleared
        
        print("ChannelName: ", channel_name)

        account_id = project['CustomerID']
        
        #Create url to extract Account of the projects
        #account_url = "https://pqrtest.2exact.com/Services/Exact.Entity.REST.svc/Account(guid\'{}\')".format(account_id)
        account_url = SERVICE_URL + "Account(guid\'{}\')".format(account_id)
        account_ = requests.get(account_url,auth=HttpNtlmAuth(usernam1,password1), headers=headers)
        
        print("Is account found? ",account_.reason)
        
        

        if account_.ok == True:
            
            accoun_reference = "OK"
            
            #Try to extract group_id of the account. It is group/team id. 
            group_id = account_.json()['d']['TextFreeField29'] #for previously created account
            
            account_name = account_.json()['d']['AccountName']
            
            print("Account is: ", account_name)
            
            new_channel = create_channel(ht,channel_name,group_id) 
            
            print("Channel created?: ",new_channel.reason)
            
            if new_channel.ok == True:
                
                new_channel_created = "OK"
                
                # Extract channel url, and update the project field TextFreeField1
                webUrl = new_channel.json()['webUrl']
                
                updated_project = requests.post(project_url,auth=HttpNtlmAuth(usernam1,password1), data=json.dumps({"TextFreeField1":"{}".format(webUrl)}),headers=header_post)
                
                if updated_project.ok == True:
                    project_updated = "OK"

                    time.sleep(8)

        
        #Log the results of previous steps
        logging.info(" ChannelName: {}, ProjectNumber: {}, AccountRefExists?: {}, NewChannel: {}, ProjectUpdated: {}".format(channel_name,project_number, accoun_reference , new_channel_created, project_updated))



def create_channels_for_opportunities():
    '''
    Creates channel for all opportunities
    '''
    
    channel_name = 'Error'
    accoun_reference = "Error"
    new_channel_created = "Error"
    project_updated = "Error"
    
    # Get the list of all projects
    ht = get_header_teams()

    opportunities_for_channels = get_opportunities_for_channels()
    
    print(opportunities_for_channels)
    
    if len(opportunities_for_channels) == 0:
        return "No opportunities to update"

    
    # Itterate through the list of projects
    for project in opportunities_for_channels:
        
        project_url = project['__metadata']['id'] 
        
        project_number = project['ProjectNumber']
        
        descr = project['Description'][:20]
    
        it_1 = re.sub("\(|\)|\,|\[|\]|\/|\:|\®|\"|\@|\©|\#|\;|\$|\.|\^|\%","",descr)
        it_1 = re.sub("'"," ",it_1)
        description_cleared = unidecode(it_1)
             
        # Create channel name, according to the naming convention ProjectNumber
        channel_name = "VK" + project['ProjectNumber'][-5:] + "-" + description_cleared
        

        account_id = project['CustomerID']
        
        #Create url to extract Account of the projects
        account_url = SERVICE_URL + "Account(guid\'{}\')".format(account_id)
        account_ = requests.get(account_url,auth=HttpNtlmAuth(usernam1,password1), headers=headers)
        
        print("Is account found? ",account_.reason)
        
        
        if account_.ok == True:
            
            accoun_reference = "OK"
            
            #Try to extract group_id of the account. It is group/team id. 
            group_id = account_.json()['d']['TextFreeField29'] #for previously created account
            
            account_name = account_.json()['d']['AccountName']
            
            print("AccountName: ",account_name)
            new_channel = create_channel(ht,channel_name,group_id) 
            
            print("Channel created?: ",new_channel.reason, new_channel.text)
            
            if new_channel.ok == True:
                
                new_channel_created = "OK"
                
                # Extract channel url, and update the project field TextFreeField1
                webUrl = new_channel.json()['webUrl']
                
                updated_project = requests.post(project_url,auth=HttpNtlmAuth(usernam1,password1), data=json.dumps({"TextFreeField1":"{}".format(webUrl)}),headers=header_post)
                
                if updated_project.ok == True:
                    
                    project_updated = "OK"
                    time.sleep(8)

        
        
        #Log the results of previous steps
        logging.info(" ChannelName: {}, ProjectNumber: {}, AccountRefExists?: {}, NewChannel: {}, ProjectUpdated: {}".format(channel_name,project_number, accoun_reference , new_channel_created, project_updated))



def get_real_opportunities_for_channels(): 
    
    # Here you need to write correct fields!!!! Ask Frank for that
    
    '''
    This function returns real opportunities (from Opportunity entity set) that we need to create channels for.
    
    TextFreeField9 eq null - this is the key for extracting those without channel in TEAMS
    startswith(Code,'VK') eq true) , VK - this is the key verkoop .....
    
    YesNoFreeField3 eq true - this is the key, if the opportunity really needs to have channel in Teams
    '''
    
    opportunity_url = SERVICE_URL + "Opportunity?$filter=(YesNoFreeField3 eq true and TextFreeField9 eq null and startswith(Code,'VK') eq true)&$top=99"
    
    opportunities_for_channels = requests.get(opportunity_url,auth=HttpNtlmAuth(usernam1,password1), headers=headers)

    results=[]
    if opportunities_for_channels.ok == True:
        if len(opportunities_for_channels.json()['d']['results']) != 0:
            results = opportunities_for_channels.json()['d']['results']

            while ("__next" in opportunities_for_channels.json()['d'].keys()):
                print("New chunk of opportunities")
                
                link_ = opportunities_for_channels.json()['d']['__next']
                
                skip_token_with_add = link_.split("true)")[1]

                print("Skip token with add: ",skip_token_with_add)
                
                if skip_token_with_add[:5] != "&$top":
                    skip = skip_token_with_add.split("&$")[1]
                    
                    
                    next_chunk_url = opportunity_url + "&$" + skip
                    print("Next chunk url: ",next_chunk_url)
                else:
                    
                    next_chunk_url = opportunity_url[:-8] + skip_token_with_add

                opportunities_for_channels = requests.get(next_chunk_url,auth=HttpNtlmAuth(usernam1,password1), headers=headers)
                
                results_tmp = opportunities_for_channels.json()['d']['results']
                results.extend(results_tmp)
        else:
            pass
               
    return results



def create_channels_for_real_opportunities():
    '''
    Creates channel for all real opportunities (Opportunity entity set)
    '''
    
    channel_name = 'Error'
    accoun_reference = "Error"
    new_channel_created = "Error"
    project_updated = "Error"
    
    # Get the list of all projects
    ht= get_header_teams()
    print("Teams Headers: ", ht)
    opportunities_for_channels = get_real_opportunities_for_channels()
    
    print(opportunities_for_channels)
    
    if len(opportunities_for_channels) == 0:
        return "No opportunities to update"

    
    # Itterate through the list of projects
    for project in opportunities_for_channels:
        
        project_url = project['__metadata']['id'] 
        
        project_number = project['Code']
        
        descr = project['Description'][:20]
    
        it_1 = re.sub("\(|\)|\,|\[|\]|\/|\:|\®|\"|\@|\©|\#|\;|\$|\.|\^|\%","",descr)
        it_1 = re.sub("'"," ",it_1)
        description_cleared = unidecode(it_1)
             
        # Create channel name, according to the naming convention ProjectNumber
        channel_name = "OPP" + project['Code'][-5:] + "-" + description_cleared
        
        print("CahnnelName: ",channel_name)
        

        account_id = project['AccountID']
        
        #Create url to extract Account of the projects
        account_url = SERVICE_URL + "Account(guid\'{}\')".format(account_id)
        account_ = requests.get(account_url,auth=HttpNtlmAuth(usernam1,password1), headers=headers)
        
        print("Is account found? ",account_.reason)
        
        
        
        if account_.ok == True:
            
            accoun_reference = "OK"
            
            #Try to extract group_id of the account. It is group/team id. 
            group_id = account_.json()['d']['TextFreeField29'] #for previously created account
            
            account_name = account_.json()['d']['AccountName']
            
            print("AccountName: ",account_name)
            new_channel = create_channel(ht,channel_name,group_id) 
            print("Channel created?: ",new_channel.reason, new_channel.text)
            
            if new_channel.ok == True:
                
                new_channel_created = "OK"
                
                # Extract channel url, and update the project field TextFreeField1
                webUrl = new_channel.json()['webUrl']

                webURL1 = urllib.parse.unquote(webUrl)


                
                updated_project = requests.post(project_url,auth=HttpNtlmAuth(usernam1,password1), data=json.dumps({"TextFreeField9":"{}".format(webURL1)}),headers=header_post)
                
                if updated_project.ok == True:
                    
                    project_updated = "OK"
                    time.sleep(10)
        
        
        #Log the results of previous steps
        logging.info(" ChannelName: {}, ProjectNumber: {}, AccountRefExists?: {}, NewChannel: {}, ProjectUpdated: {}".format(channel_name,project_number, accoun_reference , new_channel_created, project_updated))

