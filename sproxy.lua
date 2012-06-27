local http = require("socket.http")
require("json")

function invokePath(path)
  local parts = split(path, "/")
  local requiredAs = parts[2]
  local groups = split(parts[3], ",")
  return invoke(requiredAs, groups)
end

function invoke(requiredAs, userGroups)
  local urls = getAsUrl(requiredAs, userGroups)
  if urls == nil then
    spanAsi(requiredAs, userGroups)
    urls = waitForAs(requiredAs, userGroups)
  end

  return urls[1]
end

function getAsUrl(requiredAs, userGroups)
  local groups = getGroups(userGroups)
  local getAsiRequestUri = "http://localhost:5000/get_vm/" .. requiredAs .. "/for_user_with_groups/" .. groups

  r, e = http.request(getAsiRequestUri)
  
  if e == 200 then
    return json.decode(r)
  else 
    return nil
  end
end

function spanAsi(requiredAs, userGroups)
  local groups = getGroups(userGroups)
  local spanAsiRequestUri  = "http://localhost:5000//span_as/" .. requiredAs .. "/for_user_with_groups/" .. groups

  r, e = http.request{
    method = "POST",
    url = spanAsiRequestUri
  }

  return e == 202
end

function getGroups(userGroups)
 local groups = ""
  for k, v in ipairs(userGroups) do
    groups = groups .. "," .. v
  end
  groups = string.sub(groups, 2)
  return groups
end

function waitForAs(requiredAs, userGroups)
  local urls = getAsUrl(requiredAs, userGroups)
  while urls[1] == "booting" do
    --print("Waiting for VM")
    sleep(1)
    urls = getAsUrl(requiredAs, userGroups)
  end
  return urls
end

function sleep(n)
  os.execute("sleep " .. tonumber(n))
end

function split(str, pat)
   local t = {}  -- NOTE: use {n = 0} in Lua-5.0
   local fpat = "(.-)" .. pat
   local last_end = 1
   local s, e, cap = str:find(fpat, 1)
   while s do
      if s ~= 1 or cap ~= "" then
	 table.insert(t,cap)
      end
      last_end = e+1
      s, e, cap = str:find(fpat, last_end)
   end
   if last_end <= #str then
      cap = str:sub(last_end)
      table.insert(t, cap)
   end
   return t
end
