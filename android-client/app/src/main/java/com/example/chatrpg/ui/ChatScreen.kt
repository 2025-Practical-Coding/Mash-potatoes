package com.example.chatrpg.ui

import androidx.compose.foundation.Image
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.example.chatrpg.model.SenderType
import com.example.chatrpg.ui.screen.chat.ChatBubble
import com.example.chatrpg.ui.screen.chat.ChatInput
import com.example.chatrpg.viewmodel.ChatViewModel

@Composable
fun ChatScreen(viewModel: ChatViewModel = viewModel()) {
    val messages by viewModel.chatMessages.collectAsState()
    val opening by viewModel.openingMessage.collectAsState()
    val affinity by viewModel.affinity.collectAsState()
    val convCount by viewModel.convCount.collectAsState()
    val convLimit by viewModel.convLimit.collectAsState()
    val currentChar by viewModel.currentCharacter.collectAsState()
    val selectedRegion by viewModel.selectedRegion.collectAsState()

    val backgroundResId = getBackgroundForRegion(selectedRegion)

    LaunchedEffect(Unit) {
        viewModel.loadOpening()
    }

    Box(modifier = Modifier.fillMaxSize()) {
        Image(
            painter = painterResource(id = backgroundResId),
            contentDescription = null,
            contentScale = ContentScale.Crop,
            modifier = Modifier.matchParentSize()
        )

        Column(modifier = Modifier.fillMaxSize()) {
            currentChar?.let {
                Column(modifier = Modifier.padding(12.dp)) {
                    Text("${it.name} (${it.subtitle})", style = MaterialTheme.typography.titleMedium)
                    LinearProgressIndicator(
                        progress = affinity / convLimit.toFloat().coerceAtLeast(1f),
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(8.dp)
                            .padding(top = 4.dp)
                    )
                    Text("대화 횟수: $convCount / $convLimit", style = MaterialTheme.typography.labelSmall)
                }
            }

            Divider()

            LazyColumn(
                modifier = Modifier
                    .weight(1f)
                    .padding(horizontal = 8.dp),
                reverseLayout = false
            ) {
                item {
                    if (opening.isNotBlank()) {
                        Text(opening, modifier = Modifier.padding(8.dp), style = MaterialTheme.typography.bodySmall)
                    }
                }

                items(messages) { msg ->
                    ChatBubble(
                        message = msg.message,
                        isUser = msg.sender == SenderType.USER,
                        aiName = msg.aiName
                    )
                }
            }

            ChatInput(onSend = { userInput ->
                viewModel.sendMessage(userInput)
            })
        }
    }
}
