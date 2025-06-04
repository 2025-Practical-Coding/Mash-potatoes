package com.example.chatrpg.repository

import com.example.chatrpg.model.*

interface ChatRepository {
    suspend fun getOpening(): OpeningResponse
    suspend fun postChat(request: ChatRequest): ChatResponse
    suspend fun getState(): StateResponse
    suspend fun nextRegion(): NextResponse
    suspend fun getResult(): NextResponse
}