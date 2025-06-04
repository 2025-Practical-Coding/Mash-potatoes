package com.example.chatrpg.model

data class ChatResponse(
    val region: String,        // 현재 지역
    val character: CharacterInfo, // AI NPC 캐릭터 정보
    val user_input: String,    // 사용자의 입력 메시지
    val reply: String,         // AI의 응답
    val delta: Int,            // 변화량 (예: 친밀도 변화)
    val narration: String,     // 스토리 텍스트 (내러티브)
    val total_affinity: Int,   // 총 친밀도
    val conv_count: Int,       // 대화 횟수
    val conv_limit: Int        // 대화 한계
)

data class CharacterInfo(
    val slug: String,    // AI NPC 캐릭터 식별자
    val name: String,    // 캐릭터 이름
    val subtitle: String // 캐릭터 부제
)
