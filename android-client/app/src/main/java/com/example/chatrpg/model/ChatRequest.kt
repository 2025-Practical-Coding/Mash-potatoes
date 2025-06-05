package com.example.chatrpg.model

data class ChatRequest(
    val slug: String,       // AI NPC 캐릭터 식별자
    val user_input: String  // 사용자가 보낸 메시지
)
