package com.example.chatrpg

import android.os.Bundle
import android.util.Log
import android.widget.Toast
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import com.example.chatrpg.network.RetrofitInstance
import com.example.chatrpg.ui.ChatScreen
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // 앱이 실행될 때 Log 출력
        Log.d("API", "MainActivity onCreate 진입")

        // pingServer 호출 전송 전에 로그 찍기
        Log.d("API", "pingServer 호출 전송됨")

        // 서버 호출
        RetrofitInstance.api.pingServer().enqueue(object : Callback<String> {
            override fun onResponse(call: Call<String>, response: Response<String>) {
                // 응답 받은 경우
                Log.d("API", "응답: ${response.body()}")
                Toast.makeText(this@MainActivity, "응답: ${response.body()}", Toast.LENGTH_SHORT).show()
            }

            override fun onFailure(call: Call<String>, t: Throwable) {
                // 실패한 경우
                Log.e("API", "실패: ${t.message}")
                Toast.makeText(this@MainActivity, "실패: ${t.message}", Toast.LENGTH_SHORT).show()
            }
        })

        setContent {
            ChatScreen()
        }
    }
}
