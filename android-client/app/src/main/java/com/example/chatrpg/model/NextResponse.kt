package com.example.chatrpg.model

data class NextResponse(
    val game_over: Boolean,
    val result: String? = null,
    val region: String? = null,
    val characters: List<String>? = null
)
