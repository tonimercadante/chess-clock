import redis
from pathlib import Path

redis_client = redis.Redis(
    host="localhost",
    port=6379,
    db=0,
    decode_responses=True
)

# Load Lua script once
lua_path = Path(__file__).resolve().parent / "lua_scripts" / "matchmaking.lua"

with open(lua_path, "r") as f:
    MATCHMAKING_LUA = f.read()
 
