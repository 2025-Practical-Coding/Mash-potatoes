package com.example.chatrpg.repository

import com.example.chatrpg.model.*

interface ChatRepository {
    suspend fun getOpening(): OpeningResponse
    suspend fun postChat(request: ChatRequest): ChatResponse
    suspend fun getState(): ChatResponse
    suspend fun nextRegion(): ChatResponse
    suspend fun getResult(): ChatResponse
}