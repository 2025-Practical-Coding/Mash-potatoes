package com.example.chatrpg.repository

import com.example.chatrpg.model.*
import com.example.chatrpg.network.RetrofitInstance

class RealChatRepository : ChatRepository {
    override suspend fun getOpening() = RetrofitInstance.api.getOpening()
    override suspend fun postChat(request: ChatRequest) = RetrofitInstance.api.postChat(request)
    override suspend fun getState() = RetrofitInstance.api.getState()
    override suspend fun nextRegion() = RetrofitInstance.api.nextRegion()
    override suspend fun getResult() = RetrofitInstance.api.getResult()
}
