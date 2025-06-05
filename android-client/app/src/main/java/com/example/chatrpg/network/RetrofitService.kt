package com.example.chatrpg.network

import com.example.chatrpg.model.*
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.Response // Response 사용

interface RetrofitService {

    // 서버에 ping 요청을 보내는 비동기 GET 호출
    @GET("/ping")
    suspend fun pingServer(): Response<String> // 응답을 String으로 받음 (Ping 테스트용)

    // Opening 정보를 요청하는 비동기 GET 호출
    @GET("/opening")
    suspend fun getOpening(): Response<OpeningResponse>

    // 사용자가 보낸 메시지로 AI와의 대화를 진행하는 POST 요청
    @POST("/chat")
    suspend fun postChat(@Body request: ChatRequest): Response<ChatResponse> // 요청은 ChatRequest, 응답은 ChatResponse로 받음

    // 상태 정보를 요청하는 비동기 GET 호출
    @GET("/state")
    suspend fun getState(): Response<ChatResponse> // 상태 정보는 ChatResponse로 받음

    // 다음 지역으로 이동하는 비동기 POST 요청
    @POST("/next")
    suspend fun nextRegion(): Response<ChatResponse> // 다음 지역 정보도 ChatResponse로 받음

    // 결과 정보를 요청하는 비동기 GET 호출
    @GET("/result")
    suspend fun getResult(): Response<ChatResponse> // 결과 정보도 ChatResponse로 받음
}
