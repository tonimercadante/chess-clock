-- KEYS[1] = queue
-- ARGV[1] = player_id
-- ARGV[2] = rating
-- ARGV[3] = rating_range

local queue = KEYS[1]
local player_id = ARGV[1]
local rating = tonumber(ARGV[2])
local range = tonumber(ARGV[3])

local MULT = 10000000000

redis.call("ZREM", queue, player_id)

local min_score = (rating - range) * MULT
local max_score = (rating + range) * MULT + (MULT - 1)

local result = redis.call("ZRANGEBYSCORE", queue, min_score, max_score, "LIMIT", 0, 1)

if #result > 0 then
	local opponent_id = result[1]
	redis.call("ZREM", queue, opponent_id)
	return opponent_id
else
	local time_ms = redis.call("TIME")
	local now = tonumber(time_ms[1]) * 1000 + math.floor(tonumber(time_ms[2]) / 1000)
	redis.call("ZADD", queue, rating * MULT + (now % MULT), player_id)
	return nil
end
