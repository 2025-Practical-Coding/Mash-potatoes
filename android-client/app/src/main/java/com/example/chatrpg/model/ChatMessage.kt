package com.example.chatrpg.model

data class ChatMessage(
    val sender: SenderType,
    val message: String,
    val narration: String = "",
    val aiName: String? = null,
    val aiSlug: String? = null
)

enum class SenderType {
    USER, AI
}
