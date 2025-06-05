package com.example.chatrpg.model

data class GameResultResponse(
    val game_over: Boolean,
    val result: GameResult
)

data class GameResult(
    val summary: String,
    val total_allies: Int,
    val ally_list: List<String>,
    val rounds_used: Int
)