package com.example.chatrpg.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.chatrpg.model.*
import com.example.chatrpg.network.RetrofitInstance
import com.google.gson.Gson
import com.google.gson.JsonParser
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch
import okhttp3.ResponseBody
import retrofit2.Response

class ChatViewModel : ViewModel() {
    private val gson = Gson()

    private val _chatMessages = MutableStateFlow<List<ChatMessage>>(emptyList())
    val chatMessages: StateFlow<List<ChatMessage>> = _chatMessages

    private val _openingMessage = MutableStateFlow("")
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
            try {
                val response = RetrofitInstance.api.getOpening()
                if (response.isSuccessful) {
                    val opening = response.body()?.opening ?: "지역 오프닝을 불러오지 못했습니다."
                    _openingMessage.value = opening
                    val slug = response.body()?.slug
                    slug?.let {
                        _currentCharacter.value = CharacterInfo(slug = it, name = it, subtitle = "")
                    }
                } else {
                    _openingMessage.value = "Opening API 실패: ${response.code()}"
                }
            } catch (e: Exception) {
                _openingMessage.value = "서버와의 연결에 실패했습니다."
                _currentCharacter.value = null
            }
        }
    }

    fun sendMessage(userInput: String) {
        _chatMessages.value += ChatMessage(
            sender = SenderType.USER,
            message = userInput
        )

        viewModelScope.launch {
            try {
                val slug = _currentCharacter.value?.slug ?: ""
                val response: Response<ResponseBody> = RetrofitInstance.api.postChat(
                    ChatRequest(slug = slug, user_input = userInput)
                )

                if (!response.isSuccessful) {
                    _chatMessages.value += ChatMessage(
                        sender = SenderType.AI,
                        message = "서버 오류: ${response.code()} - ${response.message()}",
                        aiName = "SYSTEM"
                    )
                    return@launch
                }

                val raw = response.body()?.string() ?: return@launch
                val element = JsonParser.parseString(raw)

                when {
                    element.isJsonArray -> {
                        val list = gson.fromJson(raw, Array<ChatResponse>::class.java).toList()

                        // 1. 첫 메시지: 일반 대화
                        list.getOrNull(0)?.let {
                            _chatMessages.value += ChatMessage(
                                sender = SenderType.AI,
                                message = it.reply,
                                aiName = it.character.name,
                                aiSlug = it.character.slug
                            )
                        }

                        // 2. 두 번째 메시지: 작별 멘트
                        list.getOrNull(1)?.let {
                            _chatMessages.value += ChatMessage(
                                sender = SenderType.AI,
                                message = it.reply,
                                aiName = it.character.name,
                                aiSlug = it.character.slug,
                                isGoodbye = true // <-- ChatMessage에 필드가 있다면 사용
                            )

                            // 🎯 작별 멘트 후 다음 지역으로 이동
                            loadNextRegion()
                        }

                        // 마지막 응답 기준으로 상태 갱신
                        list.lastOrNull()?.let {
                            _affinity.value = it.total_affinity
                            _convCount.value = it.conv_count
                            _convLimit.value = it.conv_limit
                        }
                    }

                    element.isJsonObject -> {
                        val obj = element.asJsonObject

                        if (obj.has("game_over")) {
                            val result = gson.fromJson(raw, GameResultResponse::class.java)
                            _chatMessages.value += ChatMessage(
                                sender = SenderType.AI,
                                message = "게임 종료: ${result.result.summary}",
                                aiName = "SYSTEM"
                            )
                        } else {
                            val res = gson.fromJson(raw, ChatResponse::class.java)
                            _chatMessages.value += ChatMessage(
                                sender = SenderType.AI,
                                message = res.reply,
                                aiName = res.character.name,
                                aiSlug = res.character.slug
                            )
                            _affinity.value = res.total_affinity
                            _convCount.value = res.conv_count
                            _convLimit.value = res.conv_limit
                        }
                    }
                }
            } catch (e: Exception) {
                _chatMessages.value += ChatMessage(
                    sender = SenderType.AI,
                    message = "오류 발생: ${e.message}",
                    aiName = "SYSTEM"
                )
            }
        }
    }

    fun loadNextRegion() {
        viewModelScope.launch {
            try {
                val response = RetrofitInstance.api.nextRegion()
                if (response.isSuccessful) {
                    val regionName = response.body()?.region ?: "알 수 없음"
                    val characterSlugs = response.body()?.characters ?: emptyList()

                    _selectedRegion.value = regionName
                    // 필요 시 characterSlugs로도 추가 처리 가능
                } else {
                    _openingMessage.value = "지역 이동 실패: ${response.code()}"
                }
            } catch (e: Exception) {
                _openingMessage.value = "지역 전환 실패: ${e.message}"
            }
        }
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
