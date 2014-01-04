

import pika
import ast
import pymongo
import datetime
import logging
import time
import sys,traceback,socket,threading
from datetime import datetime
from time import sleep

# configuration
MONGODB_NAME = "terrydb"
HOSTNAME = ':'+socket.gethostname()
QUEUE_NAME = 'hello'
MONGODB_URL= 'mongodb://localhost'
RABBITMQ_URL='localhost'

LOG_FORMAT = ('[%(levelname)s] %(asctime)s %(name)s : %(message)s')
LOGGER = logging.getLogger(__name__)
              
class WorkerThread(threading.Thread):
    def __init__(self,threadID,name,counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
        # init rabbitmq
        # init mongodb

    # make rabbitMQ connection and create channel        
    def initRabbitMQ(self):
        self.q_conn = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_URL))
        self.q_channel =self.q_conn.channel()
        self.q_channel.queue_declare(queue=QUEUE_NAME) # create queue
    
    # make mongo db connection
    def initMongoDB(self):
        self.mongo_conn = pymongo.MongoClient(MONGODB_URL)
        self.mongo_db = self.mongo_conn[MONGODB_NAME]

    def onMessage(self,ch,method,properties,body):
        try:
            LOGGER.info(str(self.name)+" recevied "+body)
            #print str(self.name) + "[x] recevied %r" % (body,)
            json_dict = ast.literal_eval(body) # convert string to dictionary
            ## need to be fixed
            ## specify board name here
            self.writeToMongoDB('MYBOARD',json_dict)
        except ValueError:
            print 'String parsing error'
        except:
            print 'unknown error'
            traceback.print_exc(file=sys.stdout)
    
    def writeToMongoDB(self,boardname,post):
        # get board name 
        s = self.mongo_db[boardname]
        # generate uuid for the posting
        post['_id'] = self.genPostId()
        try:
            s.insert(post)
        except:
            LOGGER.error(" mongodb insert fail" + str(sys.exc_info()[0]) )
            traceback.print_exc(file=sys.stdout)

    # generate post unique id with 
    # format : YYMM{microsecond from this month 1}:{hostname}
    def genPostId(self):
        time.sleep(0.001) # intentionally sleep to remove key duplication
        dt = datetime.now()
        year = str(dt.year)[-2:]
        mon = dt.month
        if mon < 10 :
            mon = '0'+str(mon)
        else:
            mon = str(mon)
        print dt.second 
        print dt.microsecond
        uid = year+mon+ str ( int(dt.day * 24 * 60 * 60 + dt.second) * 1000 + dt.microsecond / 1000.0)
        uid = uid + HOSTNAME
        return uid
                
    def run(self):
        LOGGER.info(str(self.name)+" has been started")
        self.initRabbitMQ()
        self.initMongoDB()
        self.q_channel.basic_consume(self.onMessage,queue=QUEUE_NAME,no_ack=True)
        self.q_channel.start_consuming()        
        #while 1:
        #    time.sleep(0.01)


         
    #savePostToDB('helloboard',j)
                    

def print_usage():
    print 'usage : python worker_multithread {number of thread}'
    exit()
    
def main(argv):
    if len(argv) <2:
        print_usage()
    if argv[1].isdigit() ==False :
        print_usage()
    max_thread = int(argv[1])
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
    
    LOGGER.info('Create '+str(max_thread)+' threads ')

    threadList =[]
    for i in range(max_thread):
        t_name = "WorkerThread-"+str(i)
        t = WorkerThread(i,t_name,i)
        t.start()
        threadList.append(t)
    
if __name__ == '__main__':
    main(sys.argv)
