from flask import Flask, abort
from threading import Thread
import json
import time
import random


MAX_INTERVAL = 10

app = Flask(__name__)

as_map = {'as1': { '1' : ['g1', 'g2'], '2': ['g2']}, 'as2': {'3' : ['group3']}}

vms = {
  '1': 'http://127.0.0.1:5000/vm/1', 
  '2': 'http://127.0.0.1:5000/vm/2', 
  '3': 'http://127.0.0.1:5000/vm/3'
}

def next_vm_id():
  return str(int(max(vms.keys())) + 1)

class SpanNewVmThread(Thread):
  def __init__(self, required_as, user_groups):
    Thread.__init__(self)
    self.required_as = required_as
    self.user_groups = user_groups    
    
  def run(self):      
    vm_id = next_vm_id()         
    print "booting vm {} for {} as and {} groups".format(vm_id, self.required_as, self.user_groups)
    vms[vm_id] = 'booting'
    
    if self.required_as not in as_map.keys():
      as_map[self.required_as] = {}
    
    as_definition = as_map[self.required_as]    
    as_definition[vm_id] = self.user_groups
      
    #simulate booting    
    time.sleep(random.randint(0, MAX_INTERVAL))
    vms[vm_id] = 'http://127.0.0.1:5000/vm/{}'.format(vm_id)
    print "vm {} for {} as and {} groups started".format(vm_id, self.required_as, self.user_groups)

    
    
@app.route("/vm/<vm_id>", methods=['GET'])
def get_dump_vm_response(vm_id):
    if vm_id in vms.keys() and vms[vm_id] != 'booting':
      return "Hello from {} vm".format(vm_id)
    abort(404)

@app.route("/get_vm/<as_id>/for_user_with_groups/<groups>", methods=['GET'])
def get_as_for_user(as_id, groups):
  if as_id in as_map.keys():        
    compatible_vms = get_vm_for_user(as_map[as_id], groups)
    if len(compatible_vms) > 0:
      vms_urls = []
      for vm_id in compatible_vms:
	vms_urls.append(vms[vm_id])
      return json.dumps(vms_urls)
  abort(404)

@app.route("/span_as/<as_id>/for_user_with_groups/<user_groups>", methods=['POST'])
def span_vm_for_user(as_id, user_groups):
  job = SpanNewVmThread(as_id, user_groups.split(","))
  job.start()
  return "booting", 202

def get_vm_for_user(vms, groups):
  groups_set = set(groups.split(','))
  compatible_vms = []
  for k, v in vms.iteritems():    
    required_groups = set(v)
    if required_groups.issubset(groups_set):
	compatible_vms.append(k)
  return compatible_vms   
    
if __name__ == "__main__":
    app.run()
