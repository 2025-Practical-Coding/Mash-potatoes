package com.example.chatrpg.model

data class ChatMessage(
    val sender: SenderType,
    val message: String,
    val aiName: String? = null,
    val aiSlug: String? = null,
    val isGoodbye: Boolean = false
)

enum class SenderType {
    USER,
    AI
}
