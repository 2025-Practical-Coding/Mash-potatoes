package com.example.chatrpg.model

data class StateResponse(
    val region: String,
    val current_character: CurrentCharacterInfo?, // null 가능
    val total_remaining: Int,
    val current_remaining: Int
)

data class CurrentCharacterInfo(
    val slug: String,
    val name: String,
    val subtitle: String,
    val affinity: Int
)

data class NextRegionResponse(
    val region: String,
    val characters: List<String>
)
