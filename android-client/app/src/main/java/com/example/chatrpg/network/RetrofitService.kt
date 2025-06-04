package com.example.chatrpg.network

import com.example.chatrpg.model.*
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.Call

interface RetrofitService {
    @GET("/ping")
    fun pingServer(): Call<String>

    @GET("/opening")
    suspend fun getOpening(): OpeningResponse

    @POST("/chat")
    suspend fun postChat(@Body request: ChatRequest): ChatResponse

    @GET("/state")
    suspend fun getState(): StateResponse

    @POST("/next")
    suspend fun nextRegion(): NextResponse

    @GET("/result")
    suspend fun getResult(): NextResponse
}
