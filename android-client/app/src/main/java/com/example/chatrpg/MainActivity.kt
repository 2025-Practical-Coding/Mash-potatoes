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
        lifecycleScope.launch {
            // 1. pingServer 호출
            val pingResponse = RetrofitInstance.api.pingServer()
            if (pingResponse.isSuccessful) {
                Log.d("API", "pingServer 응답: ${pingResponse.body()}")
            } else {
                Log.e("API", "pingServer 실패: ${pingResponse.code()} - ${pingResponse.message()}")
            }

            // 2. opening 호출 (응답을 ChatResponse로 처리)
            val openingResponse = RetrofitInstance.api.getOpening()
            if (openingResponse.isSuccessful) {
                // ChatResponse 구조에 맞는 응답값을 처리
                Log.d("API", "getOpening 응답: ${openingResponse.body()?.opening}")
            } else {
                Log.e("API", "getOpening 실패: ${openingResponse.code()} - ${openingResponse.message()}")
            }

            // 3. state 호출 (응답을 ChatResponse로 처리)
            val stateResponse = RetrofitInstance.api.getState()
            if (stateResponse.isSuccessful) {
                // ChatResponse 구조에 맞는 응답값을 처리
                Log.d("API", "getState 응답: ${stateResponse.body()?.reply}")
            } else {
                Log.e("API", "getState 실패: ${stateResponse.code()} - ${stateResponse.message()}")
            }

            // 4. nextRegion 호출 (응답을 ChatResponse로 처리)
            val nextRegionResponse = RetrofitInstance.api.nextRegion()
            if (nextRegionResponse.isSuccessful) {
                // ChatResponse 구조에 맞는 응답값을 처리
                Log.d("API", "nextRegion 응답: ${nextRegionResponse.body()?.reply}")
            } else {
                Log.e("API", "nextRegion 실패: ${nextRegionResponse.code()} - ${nextRegionResponse.message()}")
            }

            // 5. result 호출 (응답을 ChatResponse로 처리)
            val resultResponse = RetrofitInstance.api.getResult()
            if (resultResponse.isSuccessful) {
                // ChatResponse 구조에 맞는 응답값을 처리
                Log.d("API", "getResult 응답: ${resultResponse.body()?.reply}")
            } else {
                Log.e("API", "getResult 실패: ${resultResponse.code()} - ${resultResponse.message()}")
            }

            // 6. postChat 호출 (사용자 메시지 전송)
            val chatRequest = ChatRequest(
                user_input = "안녕 ${openingResponse.body()?.slug ?: "default-slug"} 뭐하고 있니?",
                slug = openingResponse.body()?.slug ?: "default-slug"
            )

            val chatResponse = RetrofitInstance.api.postChat(chatRequest)
            if (chatResponse.isSuccessful) {
                val response = chatResponse.body()
                if (response != null) {
                    Log.d("API", "postChat 응답: $response")
                    // AI 응답을 UI에 반영
                }
            } else {
                Log.e("API", "postChat 실패: ${chatResponse.code()} - ${chatResponse.message()}")
            }
        }
    }
}
