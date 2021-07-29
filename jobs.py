from termcolor import colored, cprint
import sys
from printib import * 

class Job:
    def __init__(self,information,thread):
        self.information = information
        self.thread = thread

    def get_job_name(self):
        return(self.information["Name"])

class Jobs:
    __instance = None

    @staticmethod
    def get_instance():
        if Jobs.__instance == None:
            Jobs()
        return Jobs.__instance

    def __init__(self):
        if Jobs.__instance == None:
            Jobs.__instance = self
            self.jobs = {}
            self.nextjob = 0
    
    def add_value(self, value):
        self.jobs[str(self.nextjob)] = value
        self.nextjob += 1

    def unset(self, key):
        try:
            if self.jobs[key]:
                self.add_value(key, None)
        except Exception as e:
            pass

    def kill_jobs(self,key):
        t = self.jobs[key].thread
        t.do_run = False
        t.join()
        print_ok("Stopped ID job")
        del self.jobs[key]

    def kill_all_jobs(self):
        keys = self.jobs.keys()
        for k in keys:
            t = self.jobs[k].thread
            t.do_run = False
            t.join()
            print_ok("Stop ID job %s" % k)
        
        self.jobs = {}
        print_ok("Stopped all jobs")
 
    
    def get_jobs(self):
        return self.jobs

    def is_id_job(self,key):
        return key in self.jobs

    def hasjobs(self):
        return len(self.jobs) > 0
    
    def show_jobs(self):
        cprint(" Jobs (ID - Name)", 'yellow')
        print (" -----------------------")
        flag = 0
        for key, value in self.jobs.items():
            flag += 1
            if flag > 1:
                print (" |")
            sys.stdout.write(" |_")
            sys.stdout.write("%s" % key)
            sys.stdout.write(" = %s \n" % (value.get_job_name()))
        print("")