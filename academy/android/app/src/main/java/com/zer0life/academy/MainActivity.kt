package com.zer0life.academy
import android.os.Bundle
import android.content.Intent
import android.net.Uri
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.material3.*
import androidx.compose.foundation.layout.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent { MaterialTheme(colorScheme = darkColorScheme()) {
            Column(Modifier.fillMaxSize().padding(32.dp), verticalArrangement = Arrangement.Center) {
                Text("ZER0LIFE Academy", style = MaterialTheme.typography.headlineLarge)
                Text("AI Creator & Developer")
                Button(onClick = { startActivity(Intent(Intent.ACTION_VIEW, Uri.parse("https://zer0life-academy.onrender.com/dashboard"))) }) { Text("Open Academy") }
            }
        } }
    }
}
