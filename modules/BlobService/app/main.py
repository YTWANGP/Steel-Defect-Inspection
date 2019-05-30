# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for
# full license information.

from stat import S_ISREG, ST_CTIME, ST_MODE
import os, uuid, sys, time, json
from azure.storage.blob import BlockBlobService, PublicAccess, ContentSettings

import iothub_client
# pylint: disable=E0611
# Disabling linting that is not supported by Pylint for C extensions such as iothub_client. See issue https://github.com/PyCQA/pylint/issues/1955 
from iothub_client import IoTHubModuleClient, IoTHubClientError, IoTHubTransportProvider, IoTHubClientRetryPolicy
from iothub_client import IoTHubMessage, IoTHubMessageDispositionResult, IoTHubError, DeviceMethodReturnValue

import glob

block_blob_service = None
container_name = 'steeldefect'
dir_path = ''

class HubManager(object):

    def __init__(self):
        # Defines settings of the IoT SDK
        protocol = IoTHubTransportProvider.MQTT
        self.client_protocol = protocol
        self.client = IoTHubModuleClient()
        self.client.create_from_environment(protocol)
        self.client.set_option("logtrace", 1)#enables MQTT logging
        self.client.set_option("messageTimeout", 10000)

        # sets the callback when a message arrives on "input1" queue.  Messages sent to 
        # other inputs or to the default will be silently discarded.
        self.client.set_message_callback("input1", receive_message_callback, self)
        print ( "Module is now waiting for messages in the input1 queue.")

RECEIVE_CALLBACKS = 0

# receive_message_callback is invoked when an incoming message arrives on the specified  input queue
def receive_message_callback(message, HubManager):
    global RECEIVE_CALLBACKS
    global container_name
    global dir_path
    global block_blob_service
    RECEIVE_CALLBACKS += 1
    print("Received message #: "+ str(RECEIVE_CALLBACKS))
    message_buffer = message.get_bytearray()
    body=message_buffer[:len(message_buffer)].decode('utf-8')
    allTags = json.loads(body)
    #print(allTags)
    for item in allTags:
        if item["inspection_result"] == "defect":
            file_name = item["frame"] + '.jpg'
            #print(file_name)
            full_path_to_file = os.path.join(dir_path, file_name)
            print(full_path_to_file)
            if os.path.getsize(full_path_to_file) > 0:
                print("start to send " + full_path_to_file)
                # Upload the created file, use local_file_name for the blob name
                block_blob_service.create_blob_from_path(container_name, file_name, full_path_to_file, content_settings=ContentSettings(content_type='image/jpg'), progress_callback=upload_callback)
                print("Success to send " + full_path_to_file + " to Azure blob")
                os.remove(full_path_to_file)
                print("Success to revome " + full_path_to_file + "\n")

    return IoTHubMessageDispositionResult.ACCEPTED

def upload_callback(current, total):
    print('({}, {})'.format(current, total))

def main(
        filePath = "",
        accountName = "",
        accountKey = ""):
    '''
    Poll to read file path, send file to Azure Blob storage
    '''
    try:
        global dir_path
        global container_name
        global block_blob_service
        print ( "\nPython %s\n" % sys.version )
        print ( "Blob service Azure IoT Edge Module. Press Ctrl-C to exit." )
        
        # Create the BlockBlockService that is used to call the Blob service for the storage account
        
        block_blob_service = BlockBlobService(account_name=accountName, account_key=accountKey)
        #container_name ='steeldefect'
        if not block_blob_service.exists(container_name):
            block_blob_service.create_container(container_name)

        # Set the permission so the blobs are public.
        block_blob_service.set_container_acl(container_name, public_access=PublicAccess.Container)
        dir_path = filePath
        
        #clean local folder
        filelist = glob.glob(os.path.join(dir_path, "*.jpg"))
        for f in filelist:
            os.remove(f)

        hubManager = HubManager()
        
        while True:
            time.sleep(1000)
            #all entries in the directory w/ stats
            #data = (os.path.join(dir_path, fn) for fn in os.listdir(dir_path))
            #data = ((os.stat(path), path) for path in data)

            # regular files, insert creation date
            #data = ((stat[ST_CTIME], path)
            #   for stat, path in data if S_ISREG(stat[ST_MODE]))

            #for cdate, path in sorted(data):
            #    local_path = os.path.expanduser(dir_path)
            #    local_file_name = os.path.basename(path)
            #    full_path_to_file =os.path.join(local_path, local_file_name)
            #    if os.path.getsize(full_path_to_file) > 0:
            #        print("start to send " + full_path_to_file)
            #        # Upload the created file, use local_file_name for the blob name
            #        block_blob_service.create_blob_from_path(container_name, local_file_name, full_path_to_file, content_settings=ContentSettings(content_type='image/jpg'), progress_callback=upload_callback)
            #        print("Success to send " + full_path_to_file + " to Azure blob\n")
                
                
    except IoTHubError as iothub_error:
        print ( "Unexpected error %s from IoTHub" % iothub_error )            
    
    except KeyboardInterrupt:
        print ( "Blob service module stopped" )



if __name__ == '__main__':
    try:
        FILE_PATH = os.getenv('FILE_PATH',"")
        ACCOUNT_NAME = os.getenv('ACCOUNT_NAME',"")
        ACCOUNT_KEY = os.getenv('ACCOUNT_KEY',"")

    except ValueError as error:
        print ( error )
        sys.exit(1)

    main(FILE_PATH,ACCOUNT_NAME,ACCOUNT_KEY)

