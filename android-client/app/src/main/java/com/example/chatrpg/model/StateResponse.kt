package com.example.chatrpg.model

data class StateResponse(
    val region: String,
    val current_character: CharacterInfo?,
    val total_remaining: Int,
    val current_remaining: Int
)
