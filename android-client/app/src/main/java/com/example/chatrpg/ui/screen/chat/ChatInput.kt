package com.example.chatrpg.ui.screen.chat

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.text.KeyboardActions


@Composable
fun ChatInput(onSend: (String) -> Unit) {
    var text by remember { mutableStateOf("") }

    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(8.dp)
    ) {
        TextField(
            value = text,
            onValueChange = { text = it },
            placeholder = { Text("메시지를 입력하세요") },
            keyboardOptions = KeyboardOptions.Default,
            modifier = Modifier
                .weight(1f)
                .padding(4.dp),
            singleLine = true
        )

        Spacer(modifier = Modifier.width(8.dp))

        Button(
            onClick = {
                val trimmed = text.trim()
                if (trimmed.isNotEmpty()) {
                    onSend(trimmed)
                    text = ""
                }
            }
        ) {
            Text("전송")
        }
    }
}

