package com.example.chatrpg.repository

import com.example.chatrpg.model.*
import com.example.chatrpg.network.RetrofitInstance
import com.google.gson.Gson
import com.google.gson.JsonParser
import okhttp3.ResponseBody
import retrofit2.Response

class RealChatRepository : ChatRepository {

    private val gson = Gson()

    override suspend fun getOpening(): OpeningResponse {
        val response = RetrofitInstance.api.getOpening()
        if (response.isSuccessful) {
            return response.body() ?: throw Exception("Opening data is null")
        } else {
            throw Exception("Failed to fetch opening: ${response.code()} - ${response.message()}")
        }
    }

    override suspend fun postChat(request: ChatRequest): Any {
        val response = RetrofitInstance.api.postChat(request)
        return parseDynamicChatResponse(response)
    }

    override suspend fun getState(): StateResponse {
        val response = RetrofitInstance.api.getState()
        if (response.isSuccessful) {
            return response.body() ?: throw Exception("State response is null")
        } else {
            throw Exception("Failed to fetch state: ${response.code()} - ${response.message()}")
        }
    }

    override suspend fun nextRegion(): Any {
        val response = RetrofitInstance.api.nextRegion()
        return parseDynamicChatResponse(response)
    }

    override suspend fun getResult(): GameResultResponse {
        val response = RetrofitInstance.api.getResult()
        if (response.isSuccessful) {
            return response.body() ?: throw Exception("Result response is null")
        } else {
            throw Exception("Failed to fetch result: ${response.code()} - ${response.message()}")
        }
    }

    /**
     * `/chat`, `/next` 등에서 다양한 응답 형태를 처리하는 공통 로직
     */
    private fun parseDynamicChatResponse(response: Response<ResponseBody>): Any {
        if (!response.isSuccessful) {
            throw Exception("API 실패: ${response.code()} - ${response.message()}")
        }

        val raw = response.body()?.string() ?: throw Exception("응답 본문이 null입니다.")
        val jsonElement = JsonParser.parseString(raw)

        return when {
            jsonElement.isJsonArray -> {
                gson.fromJson(raw, Array<ChatResponse>::class.java).toList()
            }

            jsonElement.isJsonObject -> {
                val obj = jsonElement.asJsonObject
                when {
                    obj.has("game_over") -> {
                        gson.fromJson(raw, GameResultResponse::class.java)
                    }

                    obj.has("reply") -> {
                        gson.fromJson(raw, ChatResponse::class.java)
                    }

                    else -> throw Exception("예상치 못한 JSON 응답: $raw")
                }
            }

            else -> throw Exception("알 수 없는 응답 형식: $raw")
        }
    }
}
