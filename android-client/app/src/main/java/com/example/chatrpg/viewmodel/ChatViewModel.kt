package com.example.chatrpg.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.chatrpg.model.ChatMessage
import com.example.chatrpg.model.CharacterInfo
import com.example.chatrpg.model.SenderType
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch

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

    fun sendMessage(userInput: String) {
        _chatMessages.value += ChatMessage(
            sender = SenderType.USER,
            message = userInput
        )

        val (region, response) = when {
            userInput.contains("공허로 갈래", ignoreCase = true) -> "공허" to "공허로 이동합니다. 신비롭고 위험한 곳이에요."
            userInput.contains("숲으로 갈래", ignoreCase = true) -> "숲" to "숲으로 가는 길을 안내할게요. 조심하세요!"
            userInput.contains("도시로 갈래", ignoreCase = true) -> "도시" to "도시로 이동합니다. 활기찬 분위기를 느껴보세요."
            else -> null to "무슨 말씀이신지 잘 모르겠어요. 지역을 선택하시려면 '도시로 갈래'처럼 입력해 주세요."
        }

        region?.let { _selectedRegion.value = it }

        val character = _currentCharacter.value

        _chatMessages.value += ChatMessage(
            sender = SenderType.AI,
            message = response,
            aiName = character?.name,
            aiSlug = character?.slug
        )

        _convCount.value += 1
        _affinity.value += 1
    }

    fun setCharacter(character: CharacterInfo) {
        _currentCharacter.value = character
    }

    fun resetConversation() {
        _chatMessages.value = emptyList()
        _convCount.value = 0
        _affinity.value = 0
        _currentCharacter.value = null
        _selectedRegion.value = "도시"
    }
}
