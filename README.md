smart-proxy-pof
===============

Proof of concept implementation of Smart Proxy, able to "start" VM on demand and wait until VM is fully booted. 

Basic idea is to have static URL to the (virtual) resource connected with VM and allow user to enter this resource all the time. On the lower layer there should be cloud infrastructure, which is able to provide concrete resource implementation (in this POF we have mock implementation `atmosphere_mock.py`). Concrete resource is started when user enters to virtual resource and request waits until resource is ready, than request is forwarded into concrete resource. If there is already concrete resource up and running request is forwarded immediately.

Virtual resource URL schema
---------------------------

    http://localhost:8080/smart_proxy/{resource_id}/{required_groups}/additional/forwarded/path

`resource_id` need to be connected with concrete VM and `required_groups` are a list of credentials owned by the user (e.g. g1,g2,g3)

Why "start"
-----------

Because this proof of concept implementation only simulate booting VM up (in random time starting from 0 to 10 seconds). This simulation is implemented as simple REST service created in python and [flask](http://flask.pocoo.org/) library. See `atmosphere_mock.py` for details.

Installation
------------

Smart proxy is implemented using [lua](http://www.lua.org) [extension](http://wiki.nginx.org/HttpLuaModule ) to [nginx](http://nginx.org/). You can download already preconfigured nginx with lua from [here](http://openresty.org/). 

Additionally you need to install required lua library allowing http requests

    apt-get install liblua5.1-socket2 

lua json library from http://json.luaforge.net/
    
and python flask library

    pip install Flask
    
Following code need to be added to nginx configuration:

    worker_processes  1;
    error_log logs/error.log;
    events {
      worker_connections 1024;
    }
    http {
      #path to smart_proxy lua library and lua libraries
      lua_package_path '/home/marek/work/vphshare/smart_proxy/?.lua;/usr/share/lua/5.1/?.lua;;';
      
      #path to lua so libraries
      lua_package_cpath '/usr/lib/x86_64-linux-gnu/lua/5.1/?.so;;';

      server {
        listen 8080;        
        location /smart_proxy {                
                set $my_uri '$document_uri';

                set_by_lua $asUrl '
                    require("sproxy")                    
                    return invokePath(ngx.var.my_uri)
                ';

                proxy_pass $asUrl;
        }
      }
    }

When everything is installed you can start nginx server and python REST services:

    $NGINX_HOME/start
    python atmosphere_mock.py 
    
