package com.steamsale;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;


public class DatabaseTest {
    public static void main(String[] args) throws ClassNotFoundException {
        Class.forName("oracle.jdbc.driver.OracleDriver");
        String jdbcUrl = "jdbc:oracle:thin:@localhost:1521/XE"; // 혹은 jdbc:oracle:thin:@//localhost:1521/XE
        String username = "SAMPLE";
        String password = "1234";

        try (Connection connection = DriverManager.getConnection(jdbcUrl, username, password)) {
            System.out.println("Connected to Oracle database!");
        } catch (SQLException e) {
            e.printStackTrace();
        }
    }
}
