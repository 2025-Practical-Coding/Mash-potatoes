package com.example.chatrpg.repository

import com.example.chatrpg.model.*
import kotlinx.coroutines.delay

class MockChatRepository : ChatRepository {

    private var affinity = 0
    private var count = 0
    private val limit = 7

    private val characters = listOf(
        CharacterInfo("belveth", "벨베스", "공허의 여제"),
        CharacterInfo("chogath", "초가스", "공허의 공포"),
        CharacterInfo("kaisa", "카이사", "공허의 딸")
    )

    private var currentChar = characters.random()

    override suspend fun getOpening(): OpeningResponse {
        delay(200)
        currentChar = characters.random()
        affinity = 0
        count = 0
        val replyText = "공허 지역에서 ${currentChar.name}(${currentChar.subtitle})과 마주쳤습니다. 대화를 시작하세요."
        val narration = "모험을 시작해 보세요."
        return OpeningResponse(
            opening = "오프닝",
            slug = "null"
        )
    }

    override suspend fun postChat(request: ChatRequest): ChatResponse {
        delay(200)
        affinity += (1..4).random()
        count += 1
        val replyText = when (currentChar.slug) {
            "belveth" -> "벨베스: 당신의 감정은 흥미롭군요. 하지만 그것이 이 세계를 구할 수 있을까요?"
            "chogath" -> "초가스: 너의 말 따위는 공허에 닿지 못한다. 나는 포식만을 갈구한다."
            "kaisa" -> "카이사: 나도 예전엔 인간이었어요. 공허에서 살아남기 위해 괴물이 되었죠."
            else -> "..."
        }

        val narration = when {
            affinity > 15 -> "${currentChar.name}이(가) 당신에게 호감을 느끼기 시작합니다."
            affinity > 7 -> "${currentChar.name}이(가) 당신의 말에 관심을 보입니다."
            else -> "${currentChar.name}은(는) 여전히 경계하고 있습니다."
        }

        return ChatResponse(
            region = "공허",
            character = currentChar,
            user_input = request.user_input,
            reply = replyText,
            delta = 3,
            narration = narration,
            total_affinity = affinity,
            conv_count = count,
            conv_limit = limit
        )
    }

    override suspend fun getState(): ChatResponse {
        delay(100)
        return ChatResponse(
            region = "공허",
            character = currentChar,
            user_input = "",
            reply = "현재 상태를 확인하세요.",
            delta = 0,
            narration = "모험을 진행 중입니다.",
            total_affinity = affinity,
            conv_count = count,
            conv_limit = limit
        )
    }

    override suspend fun nextRegion(): ChatResponse {
        delay(100)
        return ChatResponse(
            region = "공허",
            character = currentChar,
            user_input = "",
            reply = "다음 지역으로 이동합니다.",
            delta = 0,
            narration = "다음 지역으로 가는 길을 안내합니다.",
            total_affinity = affinity,
            conv_count = count,
            conv_limit = limit
        )
    }

    override suspend fun getResult(): ChatResponse {
        delay(100)
        val result = if (affinity >= 15) "Game Clear" else "Game Over"
        return ChatResponse(
            region = "공허",
            character = currentChar,
            user_input = "",
            reply = "게임 결과: $result",
            delta = 0,
            narration = "모험이 끝났습니다.",
            total_affinity = affinity,
            conv_count = count,
            conv_limit = limit
        )
    }
}
