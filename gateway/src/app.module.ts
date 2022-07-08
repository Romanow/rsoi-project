import { Module } from '@nestjs/common';
import { AppConfigModule } from './config/app/config.module';
import { AuthModule } from './services/auth/auth.module';
import { ChatModule } from './services/chat/chat.module';
import { RoomModule } from './services/room/room.module';

@Module({
  imports: [AppConfigModule, AuthModule, RoomModule, ChatModule],
  controllers: [],
  providers: [],
})
export class AppModule {}
