package com.example.juegoppt;

import android.content.Intent;
import android.os.Bundle;
import android.widget.Button;
import androidx.appcompat.app.AppCompatActivity;

public class MenuActivity extends AppCompatActivity {

    Button btnJugar, btnConsultar, btnSalir;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        btnJugar     = findViewById(R.id.btnJugar);
        btnConsultar = findViewById(R.id.btnConsultar);
        btnSalir     = findViewById(R.id.btnSalir);

        btnJugar.setOnClickListener(v -> {
            Intent intent = new Intent(MenuActivity.this, JuegoActivity.class);
            startActivity(intent);
        });

        btnConsultar.setOnClickListener(v -> {
            Intent intent = new Intent(MenuActivity.this, CorreoActivity.class);
            startActivity(intent);
        });

        btnSalir.setOnClickListener(v -> {
            finishAffinity();
        });
    }
}