package com.example.chatrpg.network

import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import retrofit2.converter.scalars.ScalarsConverterFactory

object RetrofitInstance {
    private const val BASE_URL = "http://10.0.2.2:8000"

    val api: RetrofitService by lazy {
        Retrofit.Builder()
            .baseUrl(BASE_URL)
            .addConverterFactory(ScalarsConverterFactory.create()) // ✅ 먼저
            .addConverterFactory(GsonConverterFactory.create())     // 그 다음
            .build()
            .create(RetrofitService::class.java)
    }
}
