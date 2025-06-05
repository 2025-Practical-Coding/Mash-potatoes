package com.example.chatrpg.repository

import com.example.chatrpg.model.*
import com.example.chatrpg.network.RetrofitInstance
import retrofit2.Response


class RealChatRepository : ChatRepository {

    // Opening 정보를 요청하는 메서드
    override suspend fun getOpening(): OpeningResponse {
        // Retrofit을 통해 호출하고 응답을 반환
        val response: Response<OpeningResponse> = RetrofitInstance.api.getOpening()
        if (response.isSuccessful) {
            return response.body() ?: throw Exception("Opening data is null")
        } else {
            throw Exception("Failed to fetch opening: ${response.code()} - ${response.message()}")
        }
    }

    // 사용자가 보낸 메시지로 AI와의 대화를 진행하는 메서드
    override suspend fun postChat(request: ChatRequest): ChatResponse {
        val response: Response<ChatResponse> = RetrofitInstance.api.postChat(request)
        if (response.isSuccessful) {
            return response.body() ?: throw Exception("Chat response is null")
        } else {
            throw Exception("Failed to post chat: ${response.code()} - ${response.message()}")
        }
    }

    // 상태 정보를 요청하는 메서드
    override suspend fun getState(): ChatResponse {
        val response: Response<ChatResponse> = RetrofitInstance.api.getState()
        if (response.isSuccessful) {
            return response.body() ?: throw Exception("State response is null")
        } else {
            throw Exception("Failed to fetch state: ${response.code()} - ${response.message()}")
        }
    }

    // 다음 지역으로 이동하는 메서드
    override suspend fun nextRegion(): ChatResponse {
        val response: Response<ChatResponse> = RetrofitInstance.api.nextRegion()
        if (response.isSuccessful) {
            return response.body() ?: throw Exception("Next region response is null")
        } else {
            throw Exception("Failed to fetch next region: ${response.code()} - ${response.message()}")
        }
    }

    // 결과 정보를 요청하는 메서드
    override suspend fun getResult(): ChatResponse {
        val response: Response<ChatResponse> = RetrofitInstance.api.getResult()
        if (response.isSuccessful) {
            return response.body() ?: throw Exception("Result response is null")
        } else {
            throw Exception("Failed to fetch result: ${response.code()} - ${response.message()}")
        }
    }
}
