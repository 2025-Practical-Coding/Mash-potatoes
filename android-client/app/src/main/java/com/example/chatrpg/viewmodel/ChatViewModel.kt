package com.example.chatrpg.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.chatrpg.model.ChatMessage
import com.example.chatrpg.model.CharacterInfo
import com.example.chatrpg.model.SenderType
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import com.example.chatrpg.model.*
import com.example.chatrpg.network.RetrofitInstance
import kotlinx.coroutines.launch
import retrofit2.Response

class ChatViewModel : ViewModel() {

    private val _chatMessages = MutableStateFlow<List<ChatMessage>>(emptyList())
    val chatMessages: StateFlow<List<ChatMessage>> = _chatMessages

    private val _openingMessage = MutableStateFlow("처음 뵙겠습니다. 어떤 지역으로 갈까요?")
    val openingMessage: StateFlow<String> = _openingMessage

    private val _affinity = MutableStateFlow(0)
    val affinity: StateFlow<Int> = _affinity

    private val _convCount = MutableStateFlow(0)
    val convCount: StateFlow<Int> = _convCount

    private val _convLimit = MutableStateFlow(10)
    val convLimit: StateFlow<Int> = _convLimit

    private val _currentCharacter = MutableStateFlow<CharacterInfo?>(null)
    val currentCharacter: StateFlow<CharacterInfo?> = _currentCharacter

    private val _selectedRegion = MutableStateFlow("도시")
    val selectedRegion: StateFlow<String> = _selectedRegion

    fun loadOpening() {
        viewModelScope.launch {
            _openingMessage.value = "안녕하세요, 어떤 지역으로 모험을 떠나실 건가요? (도시, 숲, 공허 중 선택해주세요)"
        }
    }

    // 사용자 메시지 처리 및 서버 호출
    fun sendMessage(userInput: String) {
        // 사용자가 보낸 메시지 추가
        _chatMessages.value += ChatMessage(
            sender = SenderType.USER,
            message = userInput
        )

        // 실제 서버와 연결하여 메시지 처리
        viewModelScope.launch {
            try {
                val chatRequest = ChatRequest(
                    user_input = userInput,
                    slug = _currentCharacter.value?.slug ?: "" // 캐릭터의 slug 정보
                )

                val response: Response<ChatResponse> = RetrofitInstance.api.postChat(chatRequest)

                if (response.isSuccessful) {
                    val aiResponse = response.body()?.reply ?: "AI 응답 없음"
                    val character = response.body()?.character

                    _chatMessages.value += ChatMessage(
                        sender = SenderType.AI,
                        message = aiResponse,
                        aiName = character?.name,
                        aiSlug = character?.slug
                    )

                    // 대화 카운트와 친밀도 증가
                    _convCount.value += 1
                    _affinity.value += response.body()?.delta ?: 0
                } else {
                    _chatMessages.value += ChatMessage(
                        sender = SenderType.AI,
                        message = "서버 오류: 응답을 받지 못했습니다.",
                        aiName = "AI"
                    )
                }
            } catch (e: Exception) {
                _chatMessages.value += ChatMessage(
                    sender = SenderType.AI,
                    message = "오류 발생: ${e.message}",
                    aiName = "AI"
                )
            }
        }
    }

    // 캐릭터 설정
    fun setCharacter(character: CharacterInfo) {
        _currentCharacter.value = character
    }

    // 대화 초기화 (리셋)
    fun resetConversation() {
        _chatMessages.value = emptyList()
        _convCount.value = 0
        _affinity.value = 0
        _currentCharacter.value = null
        _selectedRegion.value = "도시"
    }
}
