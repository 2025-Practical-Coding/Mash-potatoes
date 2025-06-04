package com.example.chatrpg.model

data class ChatResponse(
    val region: String,
    val character: CharacterInfo,
    val user_input: String,
    val reply: String,
    val delta: Int,
    val narration: String,
    val total_affinity: Int,
    val conv_count: Int,
    val conv_limit: Int
)

data class CharacterInfo(
    val slug: String,
    val name: String,
    val subtitle: String
)
