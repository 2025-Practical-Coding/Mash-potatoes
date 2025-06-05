package com.example.chatrpg

import android.os.Bundle
import android.util.Log
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.lifecycle.lifecycleScope
import com.example.chatrpg.ui.ChatScreen
import com.example.chatrpg.network.RetrofitInstance
import com.example.chatrpg.model.*
import kotlinx.coroutines.launch
import com.google.gson.Gson


class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // 채팅 화면을 설정
        setContent {
            ChatScreen() // ViewModel을 자동으로 연결하여 사용
        }

        // 서버에 여러 API 호출을 보내서 연결 확인
        testServerCalls()
    }

    private fun testServerCalls() {
        val gson = Gson()

        lifecycleScope.launch {
            // 1. opening 호출
            val openingResponse = RetrofitInstance.api.getOpening()
            if (openingResponse.isSuccessful) {
                val json = gson.toJson(openingResponse.body())
                Log.d("API", "getOpening 응답(JSON): $json")
            } else {
                Log.e("API", "getOpening 실패: ${openingResponse.code()} - ${openingResponse.message()}")
            }

            // 2. state 호출
            val stateResponse = RetrofitInstance.api.getState()
            if (stateResponse.isSuccessful) {
                val json = gson.toJson(stateResponse.body())
                Log.d("API", "getState 응답(JSON): $json")
            } else {
                Log.e("API", "getState 실패: ${stateResponse.code()} - ${stateResponse.message()}")
            }

            // 3. nextRegion 호출
            val nextRegionResponse = RetrofitInstance.api.nextRegion()
            if (nextRegionResponse.isSuccessful) {
                val raw = nextRegionResponse.body()?.string()
                Log.d("API", "nextRegion 응답(JSON): $raw")
            } else {
                Log.e("API", "nextRegion 실패: ${nextRegionResponse.code()} - ${nextRegionResponse.message()}")
            }

            // 4. result 호출
            val resultResponse = RetrofitInstance.api.getResult()
            if (resultResponse.isSuccessful) {
                val json = gson.toJson(resultResponse.body())
                Log.d("API", "getResult 응답(JSON): $json")
            } else {
                Log.e("API", "getResult 실패: ${resultResponse.code()} - ${resultResponse.message()}")
            }

            // 5. postChat 호출
            val slug = openingResponse.body()?.slug ?: "default-slug"
            val chatRequest = ChatRequest(
                user_input = "안녕 $slug 뭐하고 있니?",
                slug = slug
            )
            val chatResponse = RetrofitInstance.api.postChat(chatRequest)
            if (chatResponse.isSuccessful) {
                val raw = chatResponse.body()?.string()
                Log.d("API", "postChat 응답(JSON): $raw")
            } else {
                Log.e("API", "postChat 실패: ${chatResponse.code()} - ${chatResponse.message()}")
            }
        }
    }
}
